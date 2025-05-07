import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain

# Load environment variables from .env
load_dotenv()

# Fetch the API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Make sure the API key exists
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in the environment variables")

# Initialize the LangChain ChatOpenAI model with Groq's API
llm = ChatOpenAI(
    model="llama3-8b-8192",  # Specify the model to use
    base_url="https://api.groq.com/openai/v1",  # Groq's API URL
    api_key=GROQ_API_KEY,  # Provide the API key
)

# Set up conversation memory to remember previous user inputs
memory = ConversationBufferMemory(return_messages=True)

# Create a prompt template (this is the format for the conversation)
template = """You are a helpful assistant. Please answer clearly and concisely.
Conversation history:
{history}
User: {input}
AI:"""

# Initialize the conversation chain with memory and prompt template
chat = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=PromptTemplate(input_variables=["history", "input"], template=template),
    verbose=True,  # Optional: This enables verbose logging for debugging
)

# Function to interact with Groq API via LangChain
def ask_groq(prompt: str) -> str:
    try:
        # Use ConversationChain to predict the next response
        response = chat.predict(input=prompt)
        return response
    except Exception as e:
        # Handle any errors that occur
        return f"Error: {str(e)}"
