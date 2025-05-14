import os
from langchain.vectorstores import Weaviate
from langchain.embeddings import HuggingFaceEmbeddings
from app.services.weaviate_client import get_weaviate_session
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

def create_vectorstore():
    client = get_weaviate_session()

    loader = TextLoader("app/data/faq.txt", encoding="utf-8")
    docs = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectorstore = Weaviate.from_documents(
        documents=docs,
        embedding=embeddings,
        client=client,
        index_name="SupportDocs",  # Ensure this matches the existing class in Weaviate
        text_key="text"
    )

    return vectorstore
