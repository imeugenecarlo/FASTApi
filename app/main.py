from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.groq_utils import ask_groq  # Import Groq backup logic
from app.models import Message  # Import the Message model
from app.chains.support_chain import get_chain
from app.groq_utils import create_retrieval_chain  # Import Weaviate-based retrieval chain
from app.routes import weaviate_routes

# Set up logging for better error tracking
logging.basicConfig(level=logging.INFO)
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

# Initialize the retrieval chain
try:
    retrieval_chain = create_retrieval_chain()
except Exception as e:
    logger.error(f"Failed to initialize Weaviate retrieval chain: {e}")
    retrieval_chain = None


@app.post("/chat")
async def chat(message: Message):
    try:
        if retrieval_chain:
            # Attempt to use the Weaviate-based retrieval chain
            result = retrieval_chain.invoke({"query": message.prompt})
            reply = result["result"]  # Extract the answer
        else:
            # Fall back to Groq logic if retrieval chain is unavailable
            logger.warning("Falling back to Groq logic due to unavailable Weaviate connection.")
            reply = ask_groq(message.prompt)
        return {"response": reply}
    except Exception as e:
        logger.error(f"Error during chat processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
from app.services.weaviate_client import get_weaviate_session

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

# @app.post("/chat")
# async def chat(message: Message):
#     try:
#         # Call the ask_groq function to get a response
#         reply = ask_groq(message.prompt)
#         return {"response": reply}
#     except ValueError as ve:
#         logger.error(f"ValueError: {str(ve)}")  # Log the error for debugging
#         raise HTTPException(status_code=400, detail=f"Bad request: {str(ve)}")
#     except Exception as e:
#         logger.error(f"Exception: {str(e)}")  # Log the error for debugging
#         raise HTTPException(status_code=500, detail=f"Groq failed: {str(e)}")

#@app.get("/test-weaviate-connection")
#async def test_weaviate_connection():
 #   try:
        # Check if the client is connected to Weaviate
  #      if client.is_ready():
   #         return {"message": "Weaviate is connected and ready!"}
    #    else:
     #       return {"message": "Failed to connect to Weaviate."}
    #except Exception as e:
     #   return {"error": str(e)}