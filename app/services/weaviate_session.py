import os
import weaviate

def get_weaviate_session():
    """
    Returns a Weaviate client instance for interacting with the Weaviate Cloud.
    """
    cluster_url = os.getenv("WEAVIATE_URL")  # e.g. "rAnD0mD1g1t5.something.weaviate.cloud"
    api_key = os.getenv("WEAVIATE_API_KEY")  # Your Weaviate Cloud API key, if needed

    # If you need authentication, use weaviate.auth.AuthApiKey(api_key)
    auth = weaviate.auth.AuthApiKey(api_key) if api_key else None

    client = weaviate.Client(
        url=cluster_url,
        auth_client_secret=auth,
    )
    return client
