from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = datetime.now()

class ChatResponse(BaseModel):
    message: str
    session_id: str
    agent_type: str
    timestamp: datetime = datetime.now()

class ChatHistory(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    agent_type: str 