from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query
from typing import Optional, Dict, Any
from es_helper import ElasticsearchHelper
from document_processor import PDFChunker, generate_heading_and_summary, context
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
from helper import GenAnswer
from langchain_openai import ChatOpenAI
import os

app = FastAPI()
topic_index = "topics_v1"

# Initialize the ElasticsearchHelper with config file
es_helper = ElasticsearchHelper()

@app.post("/create_index/{index_name}/")
async def create_index(
    index_name: str
):
    """
    Create an index with specified configurations.
   
    **Path Parameter:**
    - **index_name** (str): Name of the index to create.
    
    **Returns:**
    - Success or failure message with HTTP status code
   
   """
    try:
        # Call the helper method to create the index
        result = es_helper.create_index(index_name)
        
        # Check the result and raise an HTTP exception if the creation failed
        if result['status'] == 'failure':
            raise HTTPException(status_code=400, detail=result['message'])
        
        return {"message": result['message']}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.post("/ingest_file/{index_name}/")
async def ingest_file(index_name: str, file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name  # Get the temporary file path
    
    # Process the PDF
    pdf_chunker = PDFChunker(chunk_size=2000, chunk_overlap = 250) 
    chunks = pdf_chunker.process_pdf(temp_file_path)
        # Index the chunk into Elasticsearch
    topics = es_helper.index_chunk(chunks, index_name)
    topic_string = ', '.join(topics)
    es_helper.index_document(topic_index, topic_string)
    return JSONResponse(content={"message": "PDF processed and indexed successfully."})


@app.post("/{index_name}/search/", response_model=dict)
def get_answer(index_name: str, query: str, temperature: float = 0.5):

    # Generate the user query vector
    user_query_vector = es_helper.generate_embeddings(query)
    
    try:
        # Perform hybrid search
        resp = es_helper.hybrid_search(index_name=index_name, user_query=query, user_query_vector=user_query_vector)
        documents = resp['hits']['hits']
        context_list = []

        for doc in documents:
            _source = doc.get('_source', {})
            heading = _source.get('heading', 'No Heading') 
            # Extract the value from the 'content' field if it exists and is non-empty
            content_value = _source.get('content', '').strip()
            if content_value:  # Ensure it's non-empty
                context_list.append(f"Document Name: {heading}\nContent: {content_value}")
        
        context_str = "\n".join(context_list)
        gen_answer = GenAnswer()
        response = gen_answer.generate_answer(query=query, context=context_str, temperature=temperature)
        if response['status'] == 'failure':
            raise HTTPException(status_code=500, detail=response['message'])
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")

@app.post("/{index_name}/agent_search/", response_model=dict)
def get_answer_with_agent(index_name: str, query: str, temperature: float = 0.5):
    # Generate the user query vector
    user_query_vector = es_helper.generate_embeddings(query)
    
    try:
        # Perform hybrid search
        retrieved_topics = es_helper.get_topics(topic_index)
        gen_answer = GenAnswer()
        if not gen_answer.should_call_vector_db(query, retrieved_topics):
            response = gen_answer.generate_response(query)

        else:
            resp = es_helper.hybrid_search(index_name=index_name, user_query=query, user_query_vector=user_query_vector)
            documents = resp['hits']['hits']
            context_list = []

            for doc in documents:
                _source = doc.get('_source', {})
                heading = _source.get('heading', 'No Heading') 
                # Extract the value from the 'content' field if it exists and is non-empty
                content_value = _source.get('content', '').strip()
                if content_value:  # Ensure it's non-empty
                    context_list.append(f"Document Name: {heading}\nContent: {content_value}")
            
            context_str = "\n".join(context_list)
            gen_answer = GenAnswer()
            response = gen_answer.generate_answer(query=query, context=context_str, temperature=temperature)
        
        if response['status'] == 'failure':
            raise HTTPException(status_code=500, detail=response['message'])
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



