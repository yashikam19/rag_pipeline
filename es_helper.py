from elasticsearch import Elasticsearch, exceptions
import google.generativeai as genai
import json
from dotenv import load_dotenv
from document_processor import generate_heading_and_summary
import os

class ElasticsearchHelper:
    def __init__(self):
        """
        Initialize the ElasticsearchHelper class by reading the configuration and connecting to Elasticsearch.
        
        :param config_file: Path to the configuration file containing ES_URL, ES_USERNAME, and ES_PASSWORD
        """
        # Establish connection to Elasticsearch
        load_dotenv()
        self.ES_URL = os.getenv("ES_URL")
        self.ES_API = os.getenv("ES_API")
        self.es = self.connect_to_es()

    def connect_to_es(self) -> Elasticsearch:
        """
        Establish a connection to the Elasticsearch cluster using the provided credentials.

        :return: Elasticsearch client object
        """
        try:
            es = Elasticsearch(
                self.ES_URL,
                api_key=self.ES_API
            )
            # You can check connection here by pinging ES
            if es.ping():
                print("Successfully connected to Elasticsearch.")
            else:
                raise Exception("Could not connect to Elasticsearch.")
            return es
        except Exception as e:
            print(f"Error connecting to Elasticsearch: {str(e)}")
            raise

    def create_index(self, index_name: str) -> dict:
        """
        Create an Elasticsearch index with the provided index name and predefined mappings.

        :param index_name: The name of the index to create
        :return: A dictionary indicating success or failure
        """
        # Define index settings and mappings
        index_body = {
            "settings": {
                "number_of_shards": 1,  # Define number of shards
                "number_of_replicas": 0,  # Set number of replicas to 0
            },
            "mappings": {
                "properties": {
                    "content": {
                        "type": "text"
                    },
                    "heading": {
                        "type": "text"
                    },
                    "summaryVector": {
                        "type": "dense_vector",
                        "dims": 768
                    },
                    "contentVector": {
                        "type": "dense_vector",
                        "dims": 768
                    },
                    "summary": {
                        "type": "text"
                    }
                }
            }
        }

        try:
            # Check if the index already exists
            if self.es.indices.exists(index=index_name):
                return {"status": "failure", "message": f"Index {index_name} already exists."}

            # Create the index
            self.es.indices.create(index=index_name, body=index_body)
            return {"status": "success", "message": f"Index {index_name} created successfully."}
        
        except exceptions.ElasticsearchException as e:
            # Handle Elasticsearch exceptions
            return {"status": "failure", "message": f"Error creating index: {str(e)}"}
            
    def generate_embeddings(self, text):
        GOOGLE_API_KEY= "AIzaSyAuO81OuhFvmHFeB_eUov8scCSRHjpGp0M"
        genai.configure(api_key=GOOGLE_API_KEY)
        result = genai.embed_content(model="models/text-embedding-004", content=text)
        return result['embedding']

    def index_chunk(self, chunks, index_name):
        bulk_data = []
        topics = []
        for chunk in chunks:
            output = generate_heading_and_summary(chunk)

            # Clean up the output string
            json_string = output.strip().strip('```').strip('json').strip()
            python_string = output.strip().strip('```').strip('python').strip()
            # Attempt to parse the JSON
            try:
                data = json.loads(json_string)  # Try parsing as JSON first
            except json.JSONDecodeError:
                try:
                    data = json.loads(python_string)  # If that fails, try the Python format
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
            
            heading = data.get('Heading', 'No Heading Provided')
            summary = data.get('Summary', 'No Summary Provided')
            topics.append(heading)

            # Generate embeddings for the content and summary
            content_vector = self.generate_embeddings(chunk)
            summary_vector = self.generate_embeddings(summary)

            # Prepare the document body for Elasticsearch
            doc = {
                "heading": heading,
                "content": chunk,
                "summary": summary,
                "contentVector": content_vector,
                "summaryVector": summary_vector
            }

            # Prepare bulk request format
            action = {"index": {"_index": index_name}}
            bulk_data.append(action)
            bulk_data.append(doc)

        # Perform the bulk indexing
        if bulk_data:
            try:
                # The bulk method expects a newline-delimited string, so we convert the list to that format
                response = self.es.bulk(body=bulk_data, index=index_name)
                if response['errors']:
                    print(f"Errors occurred during bulk indexing: {response['errors']}")
                else:
                    print(f"Successfully indexed {len(chunks)} chunks into {index_name}")
            except exceptions.ElasticsearchException as e:
                print(f"Error during bulk indexing: {str(e)}")

        return topics
    
    def hybrid_search(self, index_name: str, user_query: str, user_query_vector, size: int = 10, text_search_weight: float = 1.0, vector_search_weight: float = 1.0) -> dict:
        query = {
            "size": size,
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": user_query,
                                "fields": ["heading", "content"],
                                "boost": text_search_weight
                            }
                        }
                    ],
                    "should": [
                        {
                            "script_score": {
                                "query": {
                                    "match_all": {}
                                },
                                "script": {
                                    "source": "cosineSimilarity(params.query_vector, 'summaryVector') + 1.0",
                                    "params": {
                                        "query_vector": user_query_vector
                                    }
                                },
                                "boost": vector_search_weight
                            }
                        }
                    ]
                }
            }
        }

        try:
            response = self.es.search(index=index_name, body=query)
            return response
        except exceptions.NotFoundError:
            raise Exception(f"Index '{index_name}' does not exist.")
        except exceptions.ElasticsearchException as e:
            return {"error": str(e)}
        
    def index_document(self, index: str, topic_string: str) -> dict:
        
        try:
            topics_doc = {
                "topics": topic_string 
            }
            response = self.es.index(index=index, body=topics_doc)
            return response
        except Exception as e:
            raise RuntimeError(f"Error indexing document: {str(e)}")
        
    def get_topics(self, index_name: str):
        try:
            # Query Elasticsearch to retrieve all topics from the topics index
            search_body = {
                "query": {
                    "match_all": {}
                }
            }
            
            # Execute the search query
            response = self.es.search(index=index_name, body=search_body)
            hits = response['hits']['hits']
            
            # Extract topics from the hits
            topics = [hit['_source']['topics'] for hit in hits]

            return topics

        except Exception as e:
            raise RuntimeError(f"Error retrieving topics: {str(e)}")

