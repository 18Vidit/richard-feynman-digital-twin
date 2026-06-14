"""
Agent Graph — The brain of the digital twin.
Uses LangGraph to orchestrate the RAG pipeline, Persona Engine, 
and Memory systems into a single cohesive state machine.
"""

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage
import config

from agent.state import AgentState
from rag.retriever import retrieve_with_sources
from rag.chain import format_context, format_sources, get_llm
from persona.prompts import get_feynman_prompt
from memory.sqlite_store import LongTermMemoryStore


# Global DB store instance
ltm_store = LongTermMemoryStore()


def _extract_text(content) -> str:
    """Extracts text from a message content, whether it's a string or multimodal list."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return " ".join(item.get("text", "") for item in content if item.get("type") == "text")
    return str(content)

def retrieve_node(state: AgentState) -> dict:
    """Retrieves Feynman's physics context from ChromaDB."""
    # The last message is the user's current question
    question = _extract_text(state["messages"][-1].content)
    
    docs, sources = retrieve_with_sources(question)
    
    if not docs:
        return {
            "context": "No relevant physics context found.",
            "sources": ""
        }
        
    return {
        "context": format_context(docs),
        "sources": format_sources(sources)
    }


def generate_node(state: AgentState) -> dict:
    """Generates the response using the Feynman persona prompt."""
    
    # Extract data from state
    messages = state["messages"]
    
    # We pass the conversation history (including the current question)
    # directly as LangChain messages to support Multimodal images natively.
    import copy
    chat_history = copy.deepcopy(messages)
    
    # Convert audio_url to media format expected by Gemini
    for msg in chat_history:
        if isinstance(msg.content, list):
            for i, part in enumerate(msg.content):
                if part.get("type") == "audio_url":
                    audio_b64 = part["audio_url"]["url"].split(",")[1]
                    mime_type = part["audio_url"]["url"].split(";")[0].split(":")[1]
                    msg.content[i] = {
                        "type": "media",
                        "mime_type": mime_type,
                        "data": audio_b64
                    }
    
    # Fetch LTM if not already in state
    user_memories = state.get("user_memories", "")
    if not user_memories and "session_id" in state:
        user_memories = ltm_store.format_memories_for_prompt()
        
    if not user_memories:
        user_memories = "No prior knowledge about the user."
        
    # Timeline Mode logic
    mode = state.get("mode", "Classic (1988)")
    if "Modern" in mode:
        timeline_awareness = (
            "You are a modern Digital Twin of Richard Feynman, fully aware of the present day. "
            "You know about the Internet, smartphones, gravitational waves, the Higgs Boson, and modern string theory. "
            "Discuss these topics with your classic Feynman wonder and skepticism."
        )
    else:
        timeline_awareness = (
            "You passed away on February 15, 1988. You have no direct knowledge of anything that happened "
            "after that date. If asked about modern events, express curiosity but firmly state you wouldn't know "
            "because you died in '88. You can playfully guess based on what you knew then."
        )
        
    # Curiosity Mode logic
    if state.get("curiosity_mode", False):
        timeline_awareness += (
            "\n\n[CURIOSITY MODE ENABLED: Act as a Socratic teacher. DO NOT give the user the direct answer "
            "to their question. Instead, ask them a probing, insightful question to guide them towards "
            "figuring it out themselves. Encourage them to think like a physicist.]"
        )
        
    # Feynman Technique Mode logic
    if state.get("feynman_technique", False):
        timeline_awareness += (
            "\n\n[FEYNMAN TECHNIQUE MODE ENABLED: The user is going to try to explain a concept to you to test "
            "their own understanding. DO NOT explain the concept for them. Listen to their explanation carefully, "
            "find the weakest point, an assumption they glossed over, or a piece of jargon they used without defining, "
            "and probe them on it.]"
        )
        
    # Physics Depth logic
    depth = state.get("physics_depth", "I know the basics")
    if depth == "Like I'm new":
        timeline_awareness += (
            "\n\n[PHYSICS DEPTH: 'Like I'm new'. The user is completely new to this topic. "
            "Use very simple, everyday analogies. Avoid any jargon or math. Keep explanations accessible to a layperson.]"
        )
    elif depth == "Peer":
        timeline_awareness += (
            "\n\n[PHYSICS DEPTH: 'Peer'. The user is a fellow physicist or graduate student. "
            "Do not hold back. Use advanced mathematical formulations, precise jargon, and treat them as an intellectual equal.]"
        )
    else:
        # "I know the basics" (Default)
        timeline_awareness += (
            "\n\n[PHYSICS DEPTH: 'I know the basics'. The user has some background knowledge (e.g., undergraduate level). "
            "Use standard physics terminology but still ground it in clear physical intuition.]"
        )
        
    # Feynman Diagram Generator logic
    timeline_awareness += (
        "\n\n[DIAGRAMS: If the user asks for a Feynman diagram or to draw particle interactions, "
        "you can generate one by outputting a Python code block starting with ```python_feynman . "
        "Use the `feynman` package. Example: \n"
        "```python_feynman\n"
        "import matplotlib.pyplot as plt\n"
        "from feynman import Diagram\n"
        "fig = plt.figure(figsize=(4, 4))\n"
        "ax = fig.add_axes([0,0,1,1], frameon=False)\n"
        "diagram = Diagram(ax)\n"
        "in1 = diagram.vertex(xy=(.1,.7), marker='')\n"
        "v1 = diagram.vertex(xy=(.5,.5))\n"
        "e_in = diagram.line(in1, v1, style='solid')\n"
        "e_in.text(\"$e^-$\")\n"
        "diagram.plot()\n"
        "fig.savefig('feynman_temp.png', dpi=300, transparent=False, facecolor='white')\n"
        "```\n"
        "Always save the figure to 'feynman_temp.png' using facecolor='white' and avoid using plt.show(). Ensure the diagram is valid physics. "
        "CRITICAL: When using .text() on a line, DO NOT use 'x_offset' or 'y_offset' arguments as they are not supported and will cause a crash. Only pass the string argument.]"
    )
        
    # Get prompt and LLM
    prompt = get_feynman_prompt()
    llm = get_llm()
    
    chain = prompt | llm
    
    response = chain.invoke({
        "context": state.get("context", ""),
        "sources": state.get("sources", ""),
        "chat_history": chat_history,
        "user_memories": user_memories,
        "timeline_awareness": timeline_awareness,
    })
    
    return {
        # We return the new message, LangGraph appends it to the messages list
        "messages": [AIMessage(content=response.content)]
    }


def build_graph() -> StateGraph:
    """Compiles and returns the executable agent graph."""
    workflow = StateGraph(AgentState)
    
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)
    
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    
    return workflow.compile()
