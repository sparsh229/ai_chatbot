import gradio as gr
import requests
import json
from typing import List, Tuple, Generator, Dict
import uuid

# Initialize session ID
session_id = str(uuid.uuid4())

def format_message(role: str, content: str) -> Dict[str, str]:
    return {"role": role, "content": content}

def stream_chat(message: str, history: List[Dict[str, str]]) -> Generator[Tuple[str, List[Dict[str, str]]], None, None]:
    url = "http://localhost:8000/api/v1/chat/stream"
    payload = {
        "message": message,
        "session_id": session_id
    }
    
    try:
        with requests.post(url, json=payload, stream=True) as response:
            response.raise_for_status()
            full_response = ""
            
            # Update history with user message
            history.append(format_message("user", message))
            
            # Stream the response
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8').replace('data: ', ''))
                        chunk = data.get('chunk', '')
                        full_response += chunk
                        # Always update the last assistant message
                        if history and history[-1]["role"] == "assistant":
                            history[-1]["content"] = full_response
                        else:
                            history.append(format_message("assistant", full_response))
                        yield "", history
                    except json.JSONDecodeError:
                        continue
            
            # Final update
            if history and history[-1]["role"] == "assistant":
                history[-1]["content"] = full_response
            else:
                history.append(format_message("assistant", full_response))
            yield "", history
            
    except Exception as e:
        yield str(e), history

# Create the Gradio interface
with gr.Blocks(title="AI Chatbot") as demo:
    gr.Markdown("# AI Chatbot with Multi-Agent Routing (LLM decides)")
    
    chatbot = gr.Chatbot(
        type="messages",
        elem_id="chatbot",
        height=600
    )
    
    with gr.Row():
        msg = gr.Textbox(
            show_label=False,
            placeholder="Enter your message here...",
            container=False
        )
    
    with gr.Row():
        submit_btn = gr.Button("Send")
        clear_btn = gr.Button("Clear")
    
    # Event handlers
    submit_btn.click(
        stream_chat,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot],
        api_name="chat"
    )
    
    msg.submit(
        stream_chat,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot],
        api_name="chat"
    )
    
    clear_btn.click(lambda: [], None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch(share=True) 