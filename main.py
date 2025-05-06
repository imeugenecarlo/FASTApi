from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq_utils import ask_groq

app = FastAPI()

# Allow frontend origin (Vite dev server, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    prompt: str

@app.post("/chat")
async def chat(message: Message):
    try:
        reply = ask_groq(message.prompt)
        return {"response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq failed: {str(e)}")
