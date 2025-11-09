"""LangGraph chat agent compatible with frontend.

A simple conversational agent that works with the LangGraph frontend.
"""
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# System prompt for the agent
SYSTEM_PROMPT = """You are a helpful and resourceful AI assistant.

You can help with a wide variety of tasks including:
- Answering questions
- Providing explanations
- Writing and analyzing code
- Creative writing
- Problem solving
- And much more!

Be concise, accurate, and helpful in your responses."""


# Define the state for the agent
class AgentState(TypedDict):
    """State for the conversational agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Initialize the LLM
model = ChatOpenAI(model="gpt-4o", temperature=0.7, streaming=True)


# Define the agent node
def call_model(state: AgentState) -> dict:
    """Call the language model with the current state."""
    messages = state["messages"]
    
    # Prepend system message if not already present
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    
    # Call the model
    response = model.invoke(messages)
    
    # Return the response to be added to state
    return {"messages": [response]}


# Build the graph
def create_agent_graph():
    """Create the agent graph."""
    workflow = StateGraph(AgentState)
    
    # Add the agent node
    workflow.add_node("agent", call_model)
    
    # Define the flow
    workflow.add_edge(START, "agent")
    workflow.add_edge("agent", END)
    
    # Compile the graph
    return workflow.compile()


# Export the compiled graph
graph = create_agent_graph()