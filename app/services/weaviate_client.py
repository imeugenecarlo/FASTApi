import os
from dotenv import load_dotenv
import requests
import logging

# Load environment variables from the .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Singleton instance
_weaviate_session = None

def get_weaviate_session():
    """
    Returns a singleton session for interacting with the Weaviate REST API.
    """
    global _weaviate_session
    if _weaviate_session is None:
        weaviate_url = os.getenv("WEAVIATE_URL")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

        if not weaviate_url or not weaviate_api_key:
            raise ValueError("WEAVIATE_URL or WEAVIATE_API_KEY is not set in the environment variables")

        # Create a session with authentication headers
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {weaviate_api_key}",
            "Content-Type": "application/json"
        })
        session.base_url = weaviate_url  # Add base URL to the session
        _weaviate_session = session

    return _weaviate_session

def is_weaviate_ready():
    """
    Checks if the Weaviate instance is ready.
    """
    session = get_weaviate_session()
    try:
        response = session.get(f"{session.base_url}/v1/.well-known/ready")
        response.raise_for_status()
        return response.json().get("status") == "ready"
    except requests.RequestException as e:
        logger.error(f"Failed to connect to Weaviate: {e}")
        return False
