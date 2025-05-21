from langchain.prompts import PromptTemplate

def get_support_prompt():
    return PromptTemplate(
        input_variables=["history", "input"],
        template="""You are a helpful assistant for a dance studio. Answer briefly and kindly.
If they ask for contact, respond: "Call 555555 500513 (open 9am–5pm)".
Never give code examples.

Conversation history:
{history}
User: {input}
AI:"""
    )

def get_rag_prompt(context, query):
    """
    Returns a standardized RAG pipeline prompt.
    """
    return f"""
    Using the following context, answer the question:

    Context:
    {context}

    Question:
    {query}
    please answer the question in danish.
    You are a helpful assistant. for Casa bailar dance studio. Give the adress, phone number, and opening hours.
    """
