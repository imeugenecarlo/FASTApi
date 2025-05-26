from pydantic import BaseModel
from typing import List, Optional

# Schema for creating a class in Weaviate
class PropertySchema(BaseModel):
    name: str
    dataType: List[str]

class ClassSchema(BaseModel):
    class_name: str
    properties: List[PropertySchema]

# Schema for adding data to a class
class DataSchema(BaseModel):
    class_name: str
    properties: dict

# Schema for querying data
class QuerySchema(BaseModel):
    class_name: str
    properties: List[str]

# Response schema for health check
class HealthCheckResponse(BaseModel):
    status: str
    error: Optional[str] = None

# Schema for chat messages
class ChatMessageSchema(BaseModel):
    sender: str
    text: str
    timestamp: str  # ISO format recommended