import os
from dotenv import load_dotenv
import logging
import weaviate

# Load environment variables from the .env file
load_dotenv()

logger = logging.getLogger(__name__)

def get_weaviate_session():
    """
    Returns a Weaviate client instance for interacting with the Weaviate Cloud.
    """
    cluster_url = os.getenv("WEAVIATE_CLOUD_URL")  # e.g. "rAnD0mD1g1t5.something.weaviate.cloud"
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
