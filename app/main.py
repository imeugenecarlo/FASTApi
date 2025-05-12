from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.groq_utils import ask_groq  # Import your Groq logic
from app.models import Message  # Import the Message model
import weaviate

# Set up logging for better error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Weaviate client (this will connect to the Docker container for Weaviate)
client = weaviate.Client("http://weaviate:8080")

# Create the class if not already created in Weaviate (run this function once)
def create_schema():
    client.schema.create_class({
        "class": "Message",
        "vectorizer": "text2vec-contextionary",  # Choose a vectorizer, can be changed
        "properties": [
            {
                "name": "prompt",
                "dataType": ["text"]
            },
            {
                "name": "response",
                "dataType": ["text"]
            }
        ]
    })


app = FastAPI()

# Allow frontend origin (Vite dev server, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(message: Message):
    try:
        # Call the ask_groq function to get a response
        reply = ask_groq(message.prompt)
        return {"response": reply}
    except ValueError as ve:
        logger.error(f"ValueError: {str(ve)}")  # Log the error for debugging
        raise HTTPException(status_code=400, detail=f"Bad request: {str(ve)}")
    except Exception as e:
        logger.error(f"Exception: {str(e)}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail=f"Groq failed: {str(e)}")

