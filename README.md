# AI Chatbot with Multi-Agent Support

This is a FastAPI-based AI chatbot that supports multiple agents, chat streaming, and chat memory using LangGraph. The LLM automatically routes each message to the most appropriate agent, and chat history is managed by LangGraph's built-in memory system.

## Features

- Multiple AI agents with different personalities and specialties
- Real-time chat streaming
- Automatic agent selection (LLM decides which agent to use)
- Chat history and memory managed by LangGraph
- Gradio interface for easy testing
- RESTful API endpoints

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the Application

1. Start the FastAPI server:
```bash
python main.py
```

2. In a separate terminal, start the Gradio interface:
```bash
python gradio_interface.py
```

## Running Tests

To run the test suite:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=.

# Run specific test file
pytest tests/test_router.py

# Run tests with verbose output
pytest -v
```

## API Endpoints

- `POST /api/v1/chat/stream`: Streaming chat endpoint that returns responses in real-time. The LLM decides which agent to use; you do not need to specify agent_type.
- `GET /api/v1/chat/history/{session_id}`: Get chat history for a session (managed by LangGraph).

## Available Agents (LLM will choose automatically)

- `general`: General-purpose AI assistant
- `creative`: Creative assistant for brainstorming and ideation
- `technical`: Technical assistant for programming and technical questions

## Testing with Gradio

The Gradio interface provides an easy way to test the chatbot. You can:
- Enter your message and receive streaming responses in real-time
- The LLM will automatically route your message to the best agent
- Clear the chat history

## Project Structure

```
.
├── main.py                 # FastAPI application
├── requirements.txt        # Project dependencies
├── gradio_interface.py     # Gradio testing interface
├── controllers/
│   └── chat_controller.py  # Chat logic and LangGraph implementation
├── models/
│   └── chat_models.py      # Pydantic models
├── routers/
│   └── chat_router.py      # API routes
└── tests/
    ├── conftest.py         # Test configuration and fixtures
    ├── test_models.py      # Model tests
    ├── test_controller.py  # Controller tests
    └── test_router.py      # Router tests
``` 