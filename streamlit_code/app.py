import streamlit as st
import requests
from app_helper import text_to_speech, preprocess_text

# Base URL for FastAPI
API_BASE_URL = "https://fastapi-deployment-suxs.onrender.com"

# Streamlit UI
st.title("📚 ReadMyDoc")
st.caption("🚀 Powered by FastAPI and Elasticsearch")

# Sidebar instructions and settings
with st.sidebar:
    st.markdown("## How to use\n"
                "1. Upload a PDF Document.\n"
                "2. The document will be processed and indexed.\n"
                "3. You can then ask questions based on the indexed document.")

    st.divider()
    st.header("Settings")

    # Adding a slider for temperature (for example purposes, you can use it in querying)
    temperature = st.slider("Response Temperature", 0.0, 1.0, 0.5,
                            help="Adjust the creativity or precision of the generated answers. "
                                 "Higher values make the system more creative.")

    st.divider()
    st.markdown("## How does it work?\n"
                "When you upload a PDF document, it will be divided into chunks and indexed for efficient retrieval. "
                "You can then search the document by querying specific information or topics.")

index_name = "sarvam_v3"
# PDF Upload and Ingestion Section
# st.header("Upload a PDF Document")
uploaded_file = st.file_uploader("Upload a PDF document", type=("pdf"))

if uploaded_file and index_name:
    if st.button("Upload PDF"):
    # Ingest the PDF document using FastAPI
        with st.spinner("Decrypting the document... 🗝️"):
            # Send the PDF file to FastAPI ingestion endpoint
            files = {
                'file': ('document.pdf', uploaded_file.getvalue(), 'application/pdf')
            }
            ingest_url = f"{API_BASE_URL}/ingest_file/{index_name}/"
            try:
                response = requests.post(ingest_url, files=files)
                response.raise_for_status()
                st.success("PDF decrypted and encoded successfully.")
            except requests.exceptions.HTTPError as e:
                st.error(f"Error uploading PDF: {e}")
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")

# Document Search Section
# st.header("Search within the Document")
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# user_query = st.text_input("Enter your search query")
user_prompt = st.chat_input(
    "Ask something about the document"
)

if user_prompt and index_name:
    # if st.button("Search Document"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    st.chat_message("user").write(user_prompt)

    with st.spinner("On the hunt... 🕵️‍♂️"):
        # Search the ingested PDF using FastAPI search endpoint
        search_url = f"{API_BASE_URL}/{index_name}/agent_search/"
        try:
            params = {'query': user_prompt, 'temperature': temperature}
            response = requests.post(search_url, params=params)
            response.raise_for_status()
            result = response.json()
            
            # Display the result
            if 'response' in result:
                bot_response = result['response']
                # clean_response = preprocess_text(bot_response)
                # text_to_speech(clean_response)
                # st.markdown(result['response'])
            else:
                # st.write("No relevant information found.")
                bot_response = "No relevant information found."
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            st.chat_message("assistant").write(bot_response)
            text_to_speech(bot_response)

        except requests.exceptions.HTTPError as e:
            st.error(f"Error during search: {e}")
        except requests.exceptions.RequestException as e:
            st.error(f"Search request failed: {e}")
