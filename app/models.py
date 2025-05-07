# /app/models.py
from pydantic import BaseModel

class Message(BaseModel):
    prompt: str
