import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain_community.vectorstores import Weaviate
from langchain.embeddings.openai import OpenAIEmbeddings
import weaviate 
from weaviate.classes.init import Auth

# Load environment variables from .env
load_dotenv()
#Local Weaviate connection
# Initialize Weaviate client
client = weaviate.connect_to_local(skip_init_checks=True)

# Uncomment the following lines if you want to connect to Weaviate Cloud
# weaviate_url = os.getenv("WEAVIATE_URL")
# weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

# client = weaviate.connect_to_weaviate_cloud(
#     cluster_url=weaviate_url,
#     auth_credentials=Auth.api_key(weaviate_api_key),
# )

try:
    if client.is_ready():
        print("Weaviate is connected and ready.")
    else:
        print("Failed to connect to Weaviate.")
except Exception as e:
    print(f"Error connecting to Weaviate: {e}")

#vectorstore = Weaviate(
 #   client=client,
  #  index_name="MyIndex",
   # text_key="content",
    #embedding=OpenAIEmbeddings()
#)

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
if the question is not clear, ask for clarification. and also if they ask for human support like asking how to contact,
just give them this number:555555 500513.
and say its only available for 9am to 5pm.
and no codes examples you are chatbot 
and you are not allowed to give any code examples.
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
        
        # Check if the response is empty or invalid
        if not response.strip():
            return "I'm sorry, I couldn't generate a response. Please try again or contact support at 555555 500513 (available 9am to 5pm)."
        
        return response
    except Exception as e:
        # Handle any errors that occur
        return f"Error: {str(e)}. Please contact support at 555555 500513 (available 9am to 5pm)."
# This function can be called from your FastAPI endpoint to get a response from Groq