import pytest
from unittest.mock import AsyncMock, patch
from controllers.chat_controller import ChatController
from models.chat_models import ChatMessage

@pytest.mark.asyncio
async def test_process_message(chat_controller, test_session_id, test_message, test_agent_type):
    with patch('langchain_openai.ChatOpenAI') as mock_llm:
        # Mock the LLM response
        mock_llm.return_value.ainvoke = AsyncMock(return_value={"content": "Test response"})
        
        response = await chat_controller.process_message(
            message=test_message,
            session_id=test_session_id,
            agent_type=test_agent_type
        )
        
        assert response.message == "Test response"
        assert response.session_id == test_session_id
        assert response.agent_type == test_agent_type
        
        # Verify chat history was updated
        assert len(chat_controller.chat_histories[test_session_id]) == 2
        assert chat_controller.chat_histories[test_session_id][0].content == test_message
        assert chat_controller.chat_histories[test_session_id][1].content == "Test response"

@pytest.mark.asyncio
async def test_process_message_stream(chat_controller, test_session_id, test_message, test_agent_type):
    with patch('langchain_openai.ChatOpenAI') as mock_llm:
        # Mock the streaming response
        mock_chunks = ["Test", " response", " streaming"]
        mock_llm.return_value.astream = AsyncMock(return_value=[
            {"content": chunk} for chunk in mock_chunks
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
        
        # Verify chat history was updated
        assert len(chat_controller.chat_histories[test_session_id]) == 2
        assert chat_controller.chat_histories[test_session_id][0].content == test_message
        assert chat_controller.chat_histories[test_session_id][1].content == "Test response streaming"

@pytest.mark.asyncio
async def test_get_chat_history(chat_controller, test_session_id):
    # Add some test messages
    chat_controller.chat_histories[test_session_id] = [
        ChatMessage(role="user", content="Hello"),
        ChatMessage(role="assistant", content="Hi there")
    ]
    
    history = await chat_controller.get_chat_history(test_session_id)
    
    assert history.session_id == test_session_id
    assert len(history.messages) == 2
    assert history.messages[0].content == "Hello"
    assert history.messages[1].content == "Hi there"

@pytest.mark.asyncio
async def test_get_chat_history_not_found(chat_controller):
    with pytest.raises(ValueError, match="Session not found"):
        await chat_controller.get_chat_history("non-existent-session") 