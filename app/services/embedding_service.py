import os
from langchain_community.vectorstores import Weaviate
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.services.weaviate_utils import get_weaviate_session
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from transformers import AutoTokenizer, AutoModel
import torch
from app.utils.logging_utils import get_logger

# Initialize logger
logger = get_logger(__name__)

# Load the Snowflake embedding model
_tokenizer = AutoTokenizer.from_pretrained("Snowflake/snowflake-arctic-embed-l-v2.0")
_model = AutoModel.from_pretrained("Snowflake/snowflake-arctic-embed-l-v2.0")

def generate_embedding(text):
    """
    Generate embeddings using the Snowflake embedding model.
    """
    inputs = _tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = _model(**inputs)
    # Use the mean pooling of the last hidden state as the embedding
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
    return embeddings

def create_vectorstore(file_path, index_name, chunk_size=500, chunk_overlap=50):
    """
    Create a vector store from a text file using the specified parameters.
    """
    client = get_weaviate_session()

    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectorstore = Weaviate.from_documents(
        documents=docs,
        embedding=embeddings,
        client=client,
        index_name=index_name,  # Ensure this matches the existing class in Weaviate
        text_key="text"
    )

    return vectorstore
