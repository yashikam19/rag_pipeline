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
    st.markdown("## How to Use\n"
            "1. **Upload Your PDF Documents**: You can upload one or multiple PDFs to get started.\n"
            "2. **Adjust Settings**: Configure the response temperature and enable sound playback to enhance your learning experience.\n"
            "3. **Ask Questions**: After uploading, you can ask questions related to the documents.")

    st.divider()
    st.header("Settings")

    play_sound = st.checkbox("🔊 Enable Sound for Responses", 
                             help="Check this box to hear audio playback of the responses. "
                                  "Perfect for auditory learners who want to listen while they learn!")
    # Adding a slider for temperature (for example purposes, you can use it in querying)
    temperature = st.slider("🌡️ Creativity Level",
                             0.0, 1.0, 0.5,
                             help="Adjust the creativity of the generated answers. "
                                  "Higher values (up to 1.0) make the responses more creative and varied, "
                                  "while lower values (down to 0.0) keep them more focused and precise.")

    st.divider()
    st.markdown("## How does it work?\n"
                "When you upload a PDF document, it will be divided into chunks and indexed for efficient retrieval.\n"
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
                st.success("PDF uploaded and ingested successfully.")
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
                if isinstance(bot_response, str) and bot_response.startswith('http'):
                    url = bot_response
                    bot_response = "Ready to test your knowledge? Here are some practice questions to help you excel! Remember, learning is a journey!"
                    st.chat_message("assistant").write(bot_response)
                    # Embed the URL
                    st.markdown(f'<iframe src="{url}" width="700" height="500"></iframe>', unsafe_allow_html=True)
                else:
                    # Display the text response
                    st.chat_message("assistant").write(bot_response)
            else:
                # st.write("No relevant information found.")
                bot_response = "No relevant information found."
                st.chat_message("assistant").write(bot_response)

            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            if play_sound:
                clean_response = preprocess_text(bot_response)
                text_to_speech(clean_response)
        except requests.exceptions.HTTPError as e:
            st.error(f"Error during search: {e}")
        except requests.exceptions.RequestException as e:
            st.error(f"Search request failed: {e}")
