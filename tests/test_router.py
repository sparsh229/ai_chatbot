import pytest
from fastapi.testclient import TestClient
import json

def test_chat_stream_endpoint(client, test_message, test_session_id, test_agent_type):
    response = client.post(
        "/api/v1/chat/stream",
        json={
            "message": test_message,
            "session_id": test_session_id,
            "agent_type": test_agent_type
        }
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    
    # Read the stream
    for line in response.iter_lines():
        if line:
            data = json.loads(line.replace('data: ', ''))
            assert "chunk" in data

def test_chat_history_endpoint(client, test_session_id):
    # First, create some chat history
    client.post(
        "/api/v1/chat/stream",
        json={
            "message": "Hello",
            "session_id": test_session_id,
            "agent_type": "general"
        }
    )
    
    # Then get the history
    response = client.get(f"/api/v1/chat/history/{test_session_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "messages" in data
    assert "agent_type" in data
    assert data["session_id"] == test_session_id
    assert len(data["messages"]) > 0

def test_chat_history_not_found(client):
    response = client.get("/api/v1/chat/history/non-existent-session")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "non-existent-session"
    assert data["messages"] == []

def test_invalid_agent_type(client, test_message, test_session_id):
    response = client.post(
        "/api/v1/chat/stream",
        json={
            "message": test_message,
            "session_id": test_session_id,
            "agent_type": "invalid_agent"
        }
    )
    assert response.status_code == 200
    # Should fallback to general agent and return a chunk
    found_chunk = False
    for line in response.iter_lines():
        if line:
            data = json.loads(line.replace('data: ', ''))
            if "chunk" in data:
                found_chunk = True
    assert found_chunk 