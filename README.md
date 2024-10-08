# ReadMyDoc

Welcome to the **RAG** project! This application demonstrates an intelligent document-based question-answering system powered by **FastAPI**, **Streamlit**, and **Elasticsearch**. The system enables efficient document search, PDF parsing & chunking, and even generates practice questions based on user queries.

### 🌐 [Streamlit Demo App](https://readmydoc.streamlit.app/)

### 📄 [FastAPI Swagger Page (deployed on Render)](https://fastapi-deployment-suxs.onrender.com)

## 🔍 Key features and techniques

* `Elasticsearch` is used as vector database to store, ingest and query documents.
* `PyPDF2` python library is used for PDF Parsing.
* Langchain's `Recursive Character Text Splitting` is used for document chunking. Default inputs are:
  - **Chunk size:** 2000 characters
  - **Chunk overlap:** 250 characters
* `Hybrid Search` using Elasticsearch combines vector search with traditional multi-match text-based search based on `content` and `heading` fields.
  - The search leverages cosine similarity between **user query embeddings** and **document embeddings** (`summaryVector`).
  - Top 10 results are retrieved and presented.
* An LLM is utilized to compute the heading and summary of each of the chunks. **Google's `text-embedding-004` model** generates the `contentVector` and `summaryVector` embeddings
* **Agentic Features**:
  - **Smart Search Agent:** Decides whether to call the vector database based on the query's relevance to precomputed document topics (headings).
  - **Practice Question Agent:** Generates practice questions for specific chapters on request.
* **Text-to-Speech Integration**: Sarvam's `Text to Speech` API brings generated responses to life with voice output.
* **Persistent Document Storage**: Uploaded PDFs are stored in Elasticsearch, so there's no need to re-upload the same file for future queries.


## ⚡ Quickstart Guide

### 🛠️ Prerequisites

1. **Python**: Ensure Python is installed. You can download it from [here](https://www.python.org/downloads/).
2. **Elasticsearch**: You'll need an Elasticsearch instance which can be set up from [here](https://www.elastic.co/cloud)

### Setup Python the environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yashikam19/rag_pipeline.git
   cd rag_pipeline
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv myenv
   myenv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the `.env` file with your API keys:
   ```bash
   OPENAI_API_KEY="<Put your token here>"
   ES_URL="<Your Elasticsearch URL>"
   ES_API="<Your Elasticsearch Authorisation>"
   ```
5. Run the app:
   ```bash
   streamlit run app.py
   ```

## 🧠 Example Queries for Streamlit App

**Question:**
Give some practice questions on chapter Sound

**Answer:**

**Question:**
Give relative speed of sound in different media

**Answer:**

**Question:**
What are laws of chemical combination of atoms.

**Answer:**



## 📘 Example Data Used

* NCERT Class 9 Sound Chapter PDF: https://drive.google.com/file/d/17jqGIlgT5yJVfIeM_-4yCMFO5Ojd8H_9/view
* NCERT Class 9 Exemplar Practice Question PDFs: https://ncert.nic.in/exemplar-problems.php?ln=en
