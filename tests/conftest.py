import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from main import app
from controllers.chat_controller import ChatController
import uuid

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def chat_controller():
    return ChatController()

@pytest.fixture
def test_session_id():
    return str(uuid.uuid4())

@pytest.fixture
def test_message():
    return "Hello, how are you?"

@pytest.fixture
def test_agent_type():
    return "general" 