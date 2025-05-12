import pytest
from unittest.mock import AsyncMock, patch
from controllers.chat_controller import ChatController
from models.chat_models import ChatMessage

@pytest.mark.asyncio
async def test_process_message_stream(chat_controller, test_session_id, test_message, test_agent_type):
    with patch('langchain_openai.ChatOpenAI') as mock_llm:
        # Mock the streaming response
        mock_chunks = ["Test response"]
        mock_llm.return_value.astream = AsyncMock(return_value=[
            {"messages": [ChatMessage(role="assistant", content=chunk)]} for chunk in mock_chunks
        ])
        
        chunks = []
        async for chunk in chat_controller.process_message_stream(
            message=test_message,
            session_id=test_session_id,
            agent_type=test_agent_type
        ):
            chunks.append(chunk)
        
        assert len(chunks) == len(mock_chunks)
        assert all("data: " in chunk for chunk in chunks)

@pytest.mark.asyncio
async def test_get_chat_history(chat_controller, test_session_id):
    # Simulate a chat by sending a message
    async for _ in chat_controller.process_message_stream(
        message="Hello",
        session_id=test_session_id,
        agent_type="general"
    ):
        pass
    history = await chat_controller.get_chat_history(test_session_id)
    assert history.session_id == test_session_id
    assert len(history.messages) >= 1
    assert history.messages[0].content == "Hello"

@pytest.mark.asyncio
async def test_get_chat_history_not_found(chat_controller):
    history = await chat_controller.get_chat_history("non-existent-session")
    assert history.session_id == "non-existent-session"
    assert history.messages == [] 