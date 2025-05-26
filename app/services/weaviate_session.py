import os
import weaviate
from weaviate.classes.init import Auth

def get_weaviate_session():
    """
    Returns a Weaviate client instance for interacting with the Weaviate Cloud.
    """
    weaviate_url = os.getenv("WEAVIATE_URL")  # e.g. "rAnD0mD1g1t5.something.weaviate.cloud"
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")  # Your Weaviate Cloud API key, if needed

    if not weaviate_url:
        raise ValueError("WEAVIATE_URL is not set")
    if not weaviate_api_key:
        raise ValueError("WEAVIATE_API_KEY is not set")

    # If you need authentication, use weaviate.auth.AuthApiKey(api_key)
    auth = weaviate.auth.AuthApiKey(weaviate_api_key) if weaviate_api_key else None

    try:
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=weaviate_url,
            auth_credentials=auth,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to connect to Weaviate: {e}")
    
    return client
