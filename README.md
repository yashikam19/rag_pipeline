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

### Setup Python environment

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
![WhatsApp Image 2024-10-08 at 18 53 13_6247c37b](https://github.com/user-attachments/assets/931096f7-b598-4527-81b6-ff092aa32f1f)

**Question:**
Give relative speed of sound in different media

**Answer:**
- The response includes exact numerical values of sound speeds in different media, quoted from the document. 
- It also provides key observations instead of directly stating the numbers.
![WhatsApp Image 2024-10-08 at 18 47 30_b08775e0](https://github.com/user-attachments/assets/527d05db-5942-4e09-a5f8-b67f5f777e8d)
![WhatsApp Image 2024-10-08 at 18 47 30_69cfbe2d](https://github.com/user-attachments/assets/b4cd9abc-6649-4705-bbcd-86ec2123f5b3)

**Question:**
What are laws of chemical combination of atoms.

**Answer:**
- Does not provide response to out of context queries
![WhatsApp Image 2024-10-08 at 18 47 28_04c13faf](https://github.com/user-attachments/assets/8ff198be-47b5-4c79-9011-ab043145f86e)

**Question:**
Explain the concept of reflection of sound.

**Answer:**
- The response includes a detailed explanation of the topic, supported by relevant examples from the text.
- It also includes activity to help clarify the concept, ensuring a deeper understanding of the topic.
![WhatsApp Image 2024-10-08 at 18 47 28_2483c257](https://github.com/user-attachments/assets/a15d56db-e835-4b1a-95b5-6549a0ceecf1)

## 📘 Dataset Used

* NCERT Class 9 Sound Chapter PDF: https://drive.google.com/file/d/17jqGIlgT5yJVfIeM_-4yCMFO5Ojd8H_9/view
* NCERT Class 9 Exemplar Practice Question PDFs: https://ncert.nic.in/exemplar-problems.php?ln=en
