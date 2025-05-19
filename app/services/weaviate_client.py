import os
from dotenv import load_dotenv
import logging
import weaviate
from datetime import datetime
from langchain.embeddings import HuggingFaceEmbeddings

# Load environment variables from the .env file
load_dotenv()
logger = logging.getLogger(__name__)

def get_weaviate_session():
    """
    Returns a Weaviate client instance for interacting with the Weaviate Cloud.
    """
    cluster_url = os.getenv("WEAVIATE_URL")  # e.g. "rAnD0mD1g1t5.something.weaviate.cloud"
    api_key = os.getenv("WEAVIATE_API_KEY")        # Your Weaviate Cloud API key, if needed

    # If you need authentication, use weaviate.classes.init.Auth.api_key(api_key)
    auth = weaviate.auth.AuthApiKey(api_key) if api_key else None

    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=cluster_url,
        auth_credentials=auth,
    )
    return client

def is_weaviate_ready():
    session = get_weaviate_session()
    try:
        return session.is_ready()
    except Exception as e:
        logger.error(f"Failed to connect to Weaviate: {e}")
        return False

def create_chat_message_class(client):
    schema = {
        "class": "ChatMessage",
        "properties": [
            {"name": "sender", "dataType": ["text"]},
            {"name": "text", "dataType": ["text"]},
            {"name": "timestamp", "dataType": ["date"]},
        ],
    }
    if not client.schema.contains({"class": "ChatMessage"}):
        client.schema.create_class(schema)

def save_chat_message(client, sender, text):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    embedding = embeddings.embed_query(text)
    data_obj = {
        "sender": sender,
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    }
    client.collections.get("ChatMessage").data.insert(
        properties=data_obj,
        vector=embedding
    )

def retrieve_chat_messages(client, query, top_k=5):
    """
    Retrieve the most relevant chat messages from Weaviate using semantic search.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    query_embedding = embeddings.embed_query(query)
    results = client.collections.get("ChatMessage").query.near_vector(
        near_vector=query_embedding,
        limit=top_k
    )
    # Each result is a WeaviateObject
    return [
        {
            "text": obj.properties["text"],
            "sender": obj.properties["sender"],
            "timestamp": obj.properties["timestamp"]
        }
        for obj in results.objects
    ]
