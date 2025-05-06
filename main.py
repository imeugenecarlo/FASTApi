from fastapi import FastAPI
from pydantic import BaseModel
from groq_utils import ask_groq

app = FastAPI()

class Message(BaseModel):
    prompt: str

@app.post("/chat")
async def chat(message: Message):
    reply = ask_groq(message.prompt)
    return {"response": reply}