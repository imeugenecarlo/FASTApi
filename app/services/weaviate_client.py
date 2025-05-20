import os
from dotenv import load_dotenv
import logging
import weaviate
from datetime import datetime
from langchain.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModel
import torch
from groq import Groq

# Load environment variables from the .env file
load_dotenv()
logger = logging.getLogger(__name__)

# Load the Snowflake embedding model
tokenizer = AutoTokenizer.from_pretrained("Snowflake/snowflake-arctic-embed-l-v2.0")
model = AutoModel.from_pretrained("Snowflake/snowflake-arctic-embed-l-v2.0")

def generate_embedding(text):
    """
    Generate embeddings using the Snowflake embedding model.
    """
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    # Use the mean pooling of the last hidden state as the embedding
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
    return embeddings

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

    # Compose prompt
    prompt = f"""
    Using the following context, answer the question:

    Context:
    {context}

    Question:
    {query}
    please answer the question in danish.
    You are a helpful assistant. for Casa bailar dance studio. Give the adress, phone number, and opening hours.
    """

    # Call Groq (you can also call it via requests.post if not using SDK)
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    answer = response.choices[0].message.content
    groq_client.close()
    return answer
