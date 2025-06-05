import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_community.vectorstores import Weaviate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
import logging
from app.services.weaviate_session import get_weaviate_session
from groq import Groq
from app.utils.logging_utils import get_logger

# Initialize logger
logger = get_logger(__name__)

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

# Set up conversation memory (global, shared for all users)
memory = ConversationBufferMemory(return_messages=True)

template = """
SYSTEM: You are a helpful AI chatbot. Follow these rules strictly:
1. If the user's question isn't clear, ask for clarification.
2. If the user asks for human support (“How do I contact…”, “I need help from an agent”), reply with:
    “For live support, please use the contact form below the chatbox or email kontakt@casabailar.”
3. Do NOT provide any code examples or use markdown formatting (no backticks, no `[text](url)` links).
4. Always give clear, concise, relevant answers. Do not repeat the user's question.
5. If you fail to generate an answer, return:
    “I'm sorry, I couldn't generate a response. Please try again or contact support at 555-555-500513 (available 9 am - 5 pm).”

CONVERSATION HISTORY:
{history}

USER: {input}
AI:
"""

# You are a helpful assistant. Please answer clearly and concisely.
# if the question is not clear, ask for clarification. and also if they ask for human support like asking how to contact,
# just give them this number:555555 500513.
# and say its only available for 9am to 5pm.
# and no codes examples you are chatbot 
# and you are not allowed to give any code examples.
# Conversation history:
# {history}
# User: {input}
# AI:"""

# Define a function to retrieve session history
def get_session_history(memory):
    return memory.load_memory_variables({}).get("history", [])

# Initialize the RunnableWithMessageHistory
chat = RunnableWithMessageHistory(
    runnable=llm,  # Pass the ChatOpenAI model as the runnable
    memory=memory,  # Use the conversation memory
    get_session_history=lambda: get_session_history(memory),  # Retrieve session history
    prompt=PromptTemplate(input_variables=["history", "input"], template=template),
    verbose=True,
)

# Define the workflow for managing conversation state
workflow = StateGraph(state_schema=MessagesState)

# Define the function that calls the model
def call_model(state: MessagesState):
    system_prompt = (
        "You are a helpful assistant. "
        "Answer all questions to the best of your ability. "
        "The provided chat history includes a summary of the earlier conversation."
    )
    system_message = SystemMessage(content=system_prompt)
    message_history = state["messages"][:-1]  # Exclude the most recent user input

    # Summarize the messages if the chat history reaches a certain size
    if len(message_history) >= 4:
        last_human_message = state["messages"][-1]
        summary_prompt = (
            "Distill the above chat messages into a single summary message. "
            "Include as many specific details as you can."
        )
        summary_message = llm.invoke(
            message_history + [HumanMessage(content=summary_prompt)]
        )

        # Delete messages that we no longer want to show up
        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"]]
        # Re-add user message
        human_message = HumanMessage(content=last_human_message.content)
        # Call the model with summary & response
        response = llm.invoke([system_message, summary_message, human_message])
        message_updates = [summary_message, human_message, response] + delete_messages
    else:
        message_updates = llm.invoke([system_message] + state["messages"])

    return {"messages": message_updates}

# Add the node and edge to the workflow
workflow.add_node("model", call_model)
workflow.add_edge(START, "model")

# Add simple in-memory checkpointer
memory_saver = MemorySaver()
app = workflow.compile(checkpointer=memory_saver)

# Function to interact with Groq API via LangChain
def ask_groq(prompt: str, history: list[str]) -> str:
    try:
        # Define the template
        template = """
SYSTEM: You are a helpful AI chatbot. Follow these rules strictly:
1. If the user's question isn't clear, ask for clarification.
2. If the user asks for human support (“How do I contact…”, “I need help from an agent”), reply with:
    “For live support, please use the contact form below the chatbox or email kontakt@casabailar.”
3. Do NOT provide any code examples or use markdown formatting (no backticks, no [text](url) links).
4. Always give clear, concise, relevant answers. Do not repeat the user's question.
5. If you fail to generate an answer, return:
    “I'm sorry, I couldn't generate a response. Please try again or contact support at 555-555-500513 (available 9 am - 5 pm).”
6. Remember to say that you can't get connection to your database to give a proper answer. Only use the fallback answer if you can't get a proper answer.
7. Always reply in Danish. You are a Danish chatbot. If the user asks in English, reply in English.

CONVERSATION HISTORY:
{history}

USER: {input}
AI:
"""

        # Format the conversation history
        formatted_history = [{"role": "user" if i % 2 == 0 else "assistant", "content": msg} for i, msg in enumerate(history)]

        # Save the formatted history into the global memory
        for message in formatted_history:
            memory.save_context({"input": message["content"]}, {})

        # Create the prompt template
        prompt_template = PromptTemplate(
            input_variables=["history", "input"],
            template=template.strip()
        )

        # Create the conversation chain using the global memory
        conversation_chain = ConversationChain(
            llm=llm,  # Use the globally initialized ChatOpenAI model
            memory=memory,  # Use the global memory instance
            prompt=prompt_template,
            verbose=False,
        )

        # Call the conversation chain with the current user input
        response = conversation_chain.predict(input=prompt)

        return response

    except Exception as e:
        logger.error(f"Groq fallback failed: {e}")
        return (
            "I'm sorry, I couldn't generate a response. "
            "Prøv igen eller ring til for menneskelig hjælp 555-555-500513 (åbent man-tors og lørdag 9 - 17 pm)."
        )


# Function to create a retrieval chain using Weaviate
def create_retrieval_chain():
    try:
        client = get_weaviate_session()
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Initialize the Weaviate vector store
        vectorstore = Weaviate(
            client=client,
            index_name="SupportDocs",  # Ensure this matches your Weaviate class name
            text_key="text",
            embedding=embeddings,
        )

        # Create a RetrievalQA chain
        retrieval_chain = RetrievalQA.from_chain_type(
            llm=llm,  # Use the ChatOpenAI model defined earlier
            retriever=vectorstore.as_retriever(),
            return_source_documents=True,  # Optional: Return source documents for debugging
        )

        return retrieval_chain
    except Exception as e:
        logger.error(f"Failed to create retrieval chain: {e}")
        return None

def call_groq(prompt, model="llama3-70b-8192", temperature=0.2):
    """
    Centralized function to interact with the Groq API.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in the environment variables")

    groq_client = Groq(api_key=api_key)
    try:
        response = groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content
    finally:
        groq_client.close()