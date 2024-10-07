from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
def generate_heading_and_summary(chunk):
    load_dotenv()
    TOKEN = os.getenv("TOKEN")
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    prompt = f"""
    You are a content specialist. Your task is to read the following text and generate a summary and a precise heading:
    
    text: {chunk}

    Provide the result in JSON format ONLY:
    "Heading": <heading>,
    "Summary": <summary>
    """
    # Set up the prompt template with LangChain

    prompt = PromptTemplate(input_variables=["text"], template=prompt)
    llm = ChatOpenAI(model="gpt-4o", default_headers={"Authorization" : TOKEN}, temperature=0)
    llm_chain = prompt | llm

    response = llm_chain.invoke({
        "text": chunk
    })
    
    return response.content

def context(response):
        documents = response['hits']
        context_list = []

        for doc in documents:
            _source = doc.get('_source', {})
            heading = _source.get('heading', 'No Heading') 
            # Extract the value from the 'content' field if it exists and is non-empty
            content_value = _source.get('content', '').strip()
            if content_value:  # Ensure it's non-empty
                context_list.append(f"Document Name: {heading}\nContent: {content_value}")
        return context_list

class PDFChunker:

    def __init__(self, chunk_size, chunk_overlap):
        self.CHUNK_SIZE = chunk_size
        self.CHUNK_OVERLAP = chunk_overlap

    def extract(self, pdf_path: str) -> str:
        # Open the PDF file from the provided path
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += f"\n {page_text} \n"
        except FileNotFoundError:
            print(f"Error: File {pdf_path} not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        return text

    def split_document(self, text):
        chunks = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = self.CHUNK_SIZE,
            chunk_overlap  = self.CHUNK_OVERLAP
        )
        docs = text_splitter.create_documents([text])
        for doc in docs:
            chunks.append(doc.page_content)
        return chunks

    def process_pdf(self, path):

        text = self.extract(path)
        # Splitting the document into chunks
        self.doc_chunks = self.split_document(text)

        # Return the chunks instead of printing
        return self.doc_chunks
