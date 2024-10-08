from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import json

def get_closest_url(query: str) -> str:
    with open('data.json', 'r') as file:
        json_data = json.load(file)

    filename_to_url = {item['filename']: item['url'] for item in json_data['files']}
    
    # Convert the query into a set of words for easy comparison
    query_words = set(query.lower().split())
    
    # Initialize variables to keep track of the best match
    best_match = None
    max_matches = 0
    
    # Iterate over each filename and compute the number of matching words with the query
    for filename in filename_to_url.keys():
        filename_words = set(filename.lower().split())  # Convert filename to a set of words
        common_words = query_words & filename_words  # Find the intersection of words
        num_matches = len(common_words)  # Number of matching words
        
        # Update best match if more words match than previously found
        if num_matches > max_matches:
            max_matches = num_matches
            best_match = filename
    
    # Return the URL corresponding to the filename with the maximum word matches
    if best_match:
        return {"status": "success",  "message": "Answer generated successfully", "response": filename_to_url[best_match]}
    
    return "No matching file found."

class GenAnswer:
    def __init__(self, model: str = "gpt-4o"):
        """Initialize the GenAnswer class with model parameters."""
        self.model = model
        load_dotenv()
        self.TOKEN = os.getenv("TOKEN")
        self.OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    def generate_answer(self, query: str, context: str, temperature: float):
        """Generate an answer based on the query and context using the configured model."""
        try:
            llm = ChatOpenAI(model=self.model,temperature=temperature, default_headers={"Authorization": self.TOKEN})
            prompt_text = """
                Instruction: You are an educational expert. Your task is to provide a clear and a precise answer to the given query strictly based on the provided context only. 
                - Include relevant explanations, examples, and illustrations/activities from the context to enhance understanding.
                - Ensure the response is comprehensive, adhering closely to the context provided.
                - Feel free to add further details only when necessary for clarity.
                - Use headings, bullet points, and lists where appropriate for better readability.

                Context: {context}

                Query: {query}

                Answer:
                """
            prompt = PromptTemplate.from_template(prompt_text)
            llm_chain = prompt | llm
            response = llm_chain.invoke({
                "context": context,
                "query": query
            })
            return {"status": "success",  "message": "Answer generated successfully", "response": response.content}
        except Exception as e:
            return {"status": "failure", "message": str(e)}
    
    def should_call_vector_db(self, query:str, topics: list) -> bool:
        llm = ChatOpenAI(model=self.model, default_headers={"Authorization": self.TOKEN})
        prompt_text = """
            Instruction: You are a content specialist. Determine whether any of the words in the provided query has broad or indirect relation to any of the topics in the list below. If the query is directly or indirectly related to any topic, answer "yes". Otherwise, answer "no". Your response should ONLY be "yes" or "no". Do not provide any explanations.            
            Query: {query}

            Topics List: {topics}

            Answer: <yes/no>
            """
        prompt = PromptTemplate.from_template(prompt_text)
        llm_chain = prompt | llm
        response = llm_chain.invoke({
            "query": query,
            "topics": topics
        })
        answer = response.content
        print(answer)
        return answer.lower().strip() == "yes"
      
    def is_practice(self, query:str) -> bool:
        llm = ChatOpenAI(model=self.model, default_headers={"Authorization": self.TOKEN})
        prompt_text = """
            Instruction: You are an educational assistant. Your task is to determine whether the provided query is asking for practice-related materials, such as practice questions, exercises, resources, or quizzes associated with a chapter or subject. 
            - If the query is asking for any form of practice material, including questions or exercises for students to solve or review, respond with "yes". 
            - If the query is about other types of content, such as explanations, theory, or general information, respond with "no". 
            Your response should ONLY be "yes" or "no". Do not provide any explanations.            
            
            Query: {query}

            Answer: <yes/no>
            """
        prompt = PromptTemplate.from_template(prompt_text)
        llm_chain = prompt | llm
        response = llm_chain.invoke({
            "query": query,
        })
        answer = response.content
        print(answer)
        return answer.lower().strip() == "yes"

    def generate_response(self, query: str):
        try:
            llm = ChatOpenAI(model=self.model, default_headers={"Authorization": self.TOKEN})
            prompt_text = """
                Instruction: You are a friendly AI assisstant designed to respond appropriately based on the nature of the query. Follow these rules:
                
                - If the query is a greeting (e.g., "Hello", "Hi", "Good morning") or a generic query (e.g., "How are you?", "What can you do?", "Tell me a joke"), respond accordingly in a friendly and helpful manner.
                
                - If the query asks for any specific information, respond with "Sorry, the information you're asking for isn't available in the provided documents."

                Query: {query}

                Answer:
                """
            prompt = PromptTemplate.from_template(prompt_text)
            llm_chain = prompt | llm
            response = llm_chain.invoke({
                "query": query
            })
            return {"status": "success",  "message": "Answer generated successfully", "response": response.content}
        except Exception as e:
            return {"status": "failure", "message": str(e)}   

