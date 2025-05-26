from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.groq_utils import ask_groq  # Import Groq backup logic
from app.models import Message  # Import the Message model
from app.chains.support_chain import get_chain  # Import the conversational retrieval chain with memory
from app.groq_utils import create_retrieval_chain  # Import Weaviate-based retrieval chain
from app.routes import weaviate_routes
from app.services.weaviate_client import get_weaviate_session, save_chat_message, rag_pipeline

# Set up logging for better error tracking
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = FastAPI()

# Include the Weaviate routes
app.include_router(weaviate_routes.router, prefix="/api", tags=["Weaviate"])

# Allow frontend origin (Vite dev server, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the conversational retrieval chain with memory
#den er ikke implementeret ordentlig, og supportdocs schema har ikke noget data. ;)
try:
    retrieval_chain = get_chain()
except Exception as e:
    logger.error(f"Failed to initialize support retrieval chain: {e}")
    retrieval_chain = None


@app.post("/chat")
async def chat(message: Message):
    try:
        # Save user message
        client = get_weaviate_session()
        save_chat_message(client, "user", message.prompt)

        # Use the RAG pipeline for response generation
        reply = rag_pipeline(client, message.prompt)

        # Save AI reply
        save_chat_message(client, "ai", reply)

        return {"response": reply}
    except Exception as e:
        logger.error(f"Error during chat processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health/weaviate")
async def health_check_weaviate():
    client = None
    try:
        client = get_weaviate_session()
        if client.is_ready():
            return {"status": "Weaviate is connected and ready"}
        else:
            return {"status": "Weaviate is not ready"}
    except Exception as e:
        return {"status": "Weaviate connection failed", "error": str(e)}
    finally:
        if client:
            client.close()