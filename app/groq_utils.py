import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

# Load environment variables from .env
load_dotenv()

# Fetch the API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Make sure the API key exists
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in the environment variables")

# Function to interact with the Groq API via LangChain
def ask_groq(prompt: str) -> str:
    
    # Initialize the LangChain ChatOpenAI model with the Groq API base URL
    llm = ChatOpenAI(
        model="llama3-8b-8192",  # Specify the model to use
        base_url="https://api.groq.com/openai/v1",  # Groq's API URL
        api_key=GROQ_API_KEY,  # Provide the API key   
    )

     # Add a note in the prompt to specify language if needed
    # For example, if we want to ensure the response is in Danish, we modify the prompt.
    if "capital of denmark" in prompt.lower():
        prompt += " Please answer in Danish."

    

    # Prepare the messages (prompt) to send to the API
    messages = [HumanMessage(content=prompt)]
    
    try:
        # Send the request to the Groq API and get the response
        response = llm(messages)
        return response.content  # Return the content of the response from the model
    except Exception as e:
        # Handle any errors in the process
        return f"Error: {str(e)}"
