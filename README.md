
# RAG Pipeline

## Demo App

(https://st-lc-rag.streamlit.app/)

## FastAPI Swagger Page (deployed on render)
https://fastapi-deployment-suxs.onrender.com

## Key features and techniques

* `Elasticsearch` is used as vector database to store, ingest and query documents.
* `PyPDF2` is used for PDF Parsing.
* `Recursive Character Text Splitting` is used for Document chunking. A default input is set to chunk size as 2000 and chunk overlap as 250.
* For efficient retrieval strategy, `hybrid search` using elasticsearch is employed. It uses `content` and `heading` fields for multi-matching along with user query. The vector search part computes the similarity score (co-sine similarity) between the `user query embeddings` and the `summaryVector` embedding fields. Top 10 search results are returned as a result
* An agent is employed to compute the heading and summary of each of the chunks. The corresponding vector embeddings are built using google's `text-embedding-004` model.
* There are 2 agentic features employed that can perform smart actions based on user query:
  - There is an agent that can decide whether to call the vector db or not. This decision is made based on whether the user query is directly related to the list of topics given. This list is formulated by embedding the individual chunk headings calculated above.
  - There is another agent that can provide practice questions for a particular chapter when asked by the user.
* Sarvam's `Text to Speech` API is used to give voice to the response generated.
* You don't have to upload the same PDF again and again, as it gets stored in the elasticsearch index once uploaded.

## Quickstart

### Setup Python Virtual environment (for Windows)

```bash
python -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt
```

### Setup .env file with API tokens needed.

```
OPENAI_API_KEY="<Put your token here>"
ES_URL="<Your Elasticsearch URL>"
ES_API="<Your Elasticsearch Authorisation>"
```

## Example Queries for Streamlit App

**Question:**
Give some practice questions on chapter Sound

**Answer:**

**Question:**
Give relative speed of sound in different media

**Answer:**

**Question:**
What are laws of chemical combination of atoms.

**Answer:**



## Example Data Used

* NCERT Class 9 Sound Chapter PDF: https://drive.google.com/file/d/17jqGIlgT5yJVfIeM_-4yCMFO5Ojd8H_9/view
* NCERT Class 9 Exemplar Practice Question PDFs: 
