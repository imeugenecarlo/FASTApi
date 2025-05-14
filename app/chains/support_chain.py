from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from app.services.embedding_service import create_vectorstore
from app.utils.prompt_templates import get_support_prompt

def get_chain():
    vectorstore = create_vectorstore()
    retriever = vectorstore.as_retriever()

    memory = ConversationBufferMemory(return_messages=True)

    chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(
            temperature=0,
            model="gpt-3.5-turbo"  # Kan være din Groq-model senere
        ),
        retriever=retriever,
        memory=memory,
        condense_question_prompt=get_support_prompt()
    )

    return chain
