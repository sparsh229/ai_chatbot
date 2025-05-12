import pytest
from datetime import datetime
from models.chat_models import ChatMessage, ChatResponse, ChatHistory

def test_chat_message_creation():
    message = ChatMessage(role="user", content="Hello")
    assert message.role == "user"
    assert message.content == "Hello"
    assert isinstance(message.timestamp, datetime)

def test_chat_response_creation():
    response = ChatResponse(
        message="Hi there",
        session_id="test-session",
        agent_type="general"
    )
    assert response.message == "Hi there"
    assert response.session_id == "test-session"
    assert response.agent_type == "general"
    assert isinstance(response.timestamp, datetime)

def test_chat_history_creation():
    messages = [
        ChatMessage(role="user", content="Hello"),
        ChatMessage(role="assistant", content="Hi there")
    ]
    history = ChatHistory(
        session_id="test-session",
        messages=messages,
        agent_type="general"
    )
    assert history.session_id == "test-session"
    assert len(history.messages) == 2
    assert history.agent_type == "general"
    assert history.messages[0].content == "Hello"
    assert history.messages[1].content == "Hi there" 