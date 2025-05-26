import os
from dotenv import load_dotenv
import logging
import weaviate
from datetime import datetime
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModel
import torch
from groq import Groq
from app.utils.prompt_templates import get_rag_prompt, get_faq_prompt
from app.services.embedding_service import generate_embedding
from app.groq_utils import call_groq
from app.services.weaviate_utils import get_weaviate_session
from app.utils.logging_utils import get_logger

# Configure logging
logging.basicConfig(level=logging.WARNING)

# Load environment variables from the .env file
load_dotenv()
logger = get_logger(__name__)

# Load the Snowflake embedding model
tokenizer = AutoTokenizer.from_pretrained("Snowflake/snowflake-arctic-embed-l-v2.0")
model = AutoModel.from_pretrained("Snowflake/snowflake-arctic-embed-l-v2.0")

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
    Retrieve the most relevant chat messages from Weaviate using hybrid search.
    """
    query_vector = generate_embedding(query)
    collection = client.collections.get("ChatMessage")
    response = collection.query.hybrid(
        query=query,
        vector=query_vector,
        limit=top_k,
        alpha=0.3,  # Adjust alpha for balancing vector and keyword search
    )
    # Prepare results
    return [
        {
            "text": obj.properties["text"],
            "sender": obj.properties["sender"],
            "timestamp": obj.properties["timestamp"]
        }
        for obj in response.objects
    ]

def rag_pipeline(client, query):
    """
    Perform a RAG pipeline to retrieve context and generate a response.
    """
    query_vector = generate_embedding(query)
    collection = client.collections.get("FAQ")

    # Hybrid Search
    response = collection.query.hybrid(
        query=query,
        vector=query_vector,
        limit=10,
        alpha=0.3,
    )

    # Prepare context
    retrieved_texts = [
        f"Category: {obj.properties['combined']}"
        for obj in response.objects
    ]
    context = "\n".join(retrieved_texts)

    # Compose prompt using FAQ-specific template
    prompt = get_faq_prompt(context, query)

    # Call Groq using centralized utility
    answer = call_groq(prompt)

    return answer
