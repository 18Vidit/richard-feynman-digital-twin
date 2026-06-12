"""
Agent State — Defines the memory passing structure for LangGraph.
"""

from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """The state graph for the Feynman Digital Twin."""
    
    # We use add_messages so LangGraph automatically appends new messages 
    # rather than overwriting the whole list.
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Retrieved chunks of Feynman's knowledge
    context: str
    
    # Sources used in the current generation
    sources: str
    
    # Formatted string of long-term user memories
    user_memories: str
    
    # Session ID for looking up SQLite memories
    session_id: str
    
    # Timeline mode ("Classic (1988)" or "Modern (Present Day)")
    mode: str
    
    # Curiosity Mode (Socratic teaching)
    curiosity_mode: bool
    
    # Feynman Technique Mode (Probe user's explanation)
    feynman_technique: bool
    
    # Physics Depth ("Like I'm new", "I know the basics", "Peer")
    physics_depth: str
