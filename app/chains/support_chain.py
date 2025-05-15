from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from app.services.embedding_service import create_vectorstore
from app.utils.prompt_templates import get_support_prompt
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch the API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_chain():
    vectorstore = create_vectorstore()
    retriever = vectorstore.as_retriever()

    memory = ConversationBufferMemory(return_messages=True)

    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(
            model="llama3-8b-8192",  # Specify the model to use
            base_url="https://api.groq.com/openai/v1",  # Groq's API URL
            api_key=GROQ_API_KEY,  # Provide the API key
        ),
        retriever=retriever,
        memory=memory,
        condense_question_prompt=get_support_prompt()
    )

    return chain