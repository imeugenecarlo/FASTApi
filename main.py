from fastapi import FastAPI, Request
from pydantic import BaseModel
from openai_utils import ask_chatgpt

app = FastAPI()

class Message(BaseModel):
    prompt: str

@app.post("/chat")
async def chat(message: Message):
    response = ask_chatgpt(message.prompt)
    return {"response": response}
