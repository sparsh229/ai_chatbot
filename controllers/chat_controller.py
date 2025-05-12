from typing import AsyncGenerator, Optional
import uuid
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END, add_messages
from langgraph.checkpoint.memory import MemorySaver
from models.chat_models import ChatMessage, ChatHistory
import json
from typing_extensions import TypedDict, Annotated, List
import os
import logging

# Define the state for LangGraph with built-in message management
class State(TypedDict):
    messages: Annotated[List, add_messages]

class ChatController:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.7, model="openai/gpt-4.1-mini",api_key=os.getenv("GITHUB_TOKEN"),base_url="https://models.github.ai/inference")
        self.setup_agents()
        self.workflow = self._build_workflow()
        self.save_workflow_graph()
        self.logger = logging.getLogger("chat_controller")

    def setup_agents(self):
        self.agent_prompts = {
            "general": ChatPromptTemplate.from_messages([
                ("system", "You are a helpful AI assistant."),
                ("human", "{input}")
            ]),
            "creative": ChatPromptTemplate.from_messages([
                ("system", "You are a creative AI assistant that helps with brainstorming and ideation."),
                ("human", "{input}")
            ]),
            "technical": ChatPromptTemplate.from_messages([
                ("system", "You are a technical AI assistant that helps with programming and technical questions."),
                ("human", "{input}")
            ])
        }
        self.agent_types = list(self.agent_prompts.keys())

    def _build_workflow(self):
        workflow = StateGraph(State)

        def router_node(state: State):
            router_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a router that decides which agent should answer a user's question.\n"
                            "Available agents: general, creative, technical.\n"
                            "Return ONLY the agent name (general, creative, or technical) as a single word."),
                ("human", "{input}")
            ])
            chain = router_prompt | self.llm
            # Use the last human message for routing
            last_human = [m for m in state["messages"] if isinstance(m, HumanMessage)][-1]
            response = chain.invoke({"input": last_human.content})
            agent_type = response.content.strip().lower()
            print(agent_type, "agent type")
            if agent_type not in self.agent_types:
                agent_type = "general"
            return {"agent_type": agent_type}

        def agent_node(agent_type):
            def node(state: State):
                prompt = self.agent_prompts[agent_type]
                chain = prompt | self.llm
                # Use all messages for context
                response = chain.invoke({"input": state["messages"][-1].content})
                return {"messages": [AIMessage(content=response.content)]}  # Do NOT return agent_type
            return node

        workflow.add_node("router", router_node)
        for agent_type in self.agent_types:
            workflow.add_node(agent_type, agent_node(agent_type))
        workflow.set_entry_point("router")
        # Use conditional edges so only the selected agent runs
        workflow.add_conditional_edges(
            "router",
            lambda state: state["agent_type"],
            {agent_type: agent_type for agent_type in self.agent_types}
        )
        for agent_type in self.agent_types:
            workflow.add_edge(agent_type, END)
        return workflow.compile(checkpointer=MemorySaver())

    async def process_message_stream(
        self,
        message: str,
        session_id: Optional[str] = None,
        agent_type: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        if not session_id:
            session_id = str(uuid.uuid4())
        state = {"messages": [HumanMessage(content=message)]}
        config = {"configurable": {"thread_id": session_id}, "stream_mode": "values"}
        full_response = ""
        try:
            found_chunk = False
            async for event in self.workflow.astream(state, config):
                print(event)
                # Iterate through all node results in the event
                for node_result in event.values():
                    if isinstance(node_result, dict) and "messages" in node_result:
                        ai_msgs = [m for m in node_result["messages"] if isinstance(m, AIMessage)]
                        if ai_msgs:
                            chunk = ai_msgs[-1].content
                            full_response += chunk
                            found_chunk = True
                            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            if not found_chunk:
                self.logger.warning(f"No AI response chunk found for message: {message}")
                yield f"data: {json.dumps({'chunk': '[No response from AI agent]'})}\n\n"
        except Exception as e:
            self.logger.error(f"Error in process_message_stream: {e}")
            yield f"data: {json.dumps({'chunk': '[Error: ' + str(e) + ']'})}\n\n"

    async def get_chat_history(self, session_id: str) -> ChatHistory:
        config = {"configurable": {"thread_id": session_id}}
        state = self.workflow.get_state(config=config)
        # Convert LangChain messages to ChatMessage models
        messages = []
        for m in state.values.get("messages", []):
            if isinstance(m, HumanMessage):
                messages.append(ChatMessage(role="user", content=m.content))
            elif isinstance(m, AIMessage):
                messages.append(ChatMessage(role="assistant", content=m.content))
        return ChatHistory(
            session_id=session_id,
            messages=messages,
            agent_type="general"  # Default agent type
        )

    def save_workflow_graph(self, filename="workflow_graph.png"):
        """Save the workflow graph as a PNG image using Graphviz."""
        graph = self.workflow.get_graph()
        graph.draw_png(filename)
        print(f"Workflow graph saved as {filename}. Open this file to view the workflow diagram.") 