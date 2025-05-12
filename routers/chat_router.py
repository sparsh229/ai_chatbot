from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
from pydantic import BaseModel
from controllers.chat_controller import ChatController
from models.chat_models import ChatMessage, ChatResponse

router = APIRouter()
chat_controller = ChatController()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        return StreamingResponse(
            chat_controller.process_message_stream(
                message=request.message,
                session_id=request.session_id
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        history = await chat_controller.get_chat_history(session_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 