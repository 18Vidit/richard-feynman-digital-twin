"""
Digital Twin of Richard Feynman — Main Streamlit UI  
Redesigned UI with three-column layout, custom message bubbles,
Feynman lecture hall aesthetic. No sidebar, no emoji, no st.chat_message.
"""

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

# Must be the first Streamlit command
st.set_page_config(
    page_title="Richard P. Feynman",
    page_icon="⚛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import re
import datetime
import importlib
import config
importlib.reload(config)
import agent.graph
import rag.chain
importlib.reload(rag.chain)
importlib.reload(agent.graph)
from agent.graph import build_graph
from persona.formatter import format_chat_message
from memory.sqlite_store import LongTermMemoryStore

# UI modules
from ui.styles import inject_css
from ui.header import render_header, render_mode_toggle
from ui.left_panel import render_left_panel
from ui.chat_components import render_chat_message, render_thinking_bubble, render_suggestions
from ui.right_panel import render_right_panel

# Render Loading Screen Immediately
inject_css()

st.markdown("""
<div class="splash-screen">
    <img class="splash-portrait" src="https://upload.wikimedia.org/wikipedia/en/4/42/Richard_Feynman_Nobel.jpg" />
    <div class="splash-title">Richard P. Feynman</div>
    <div class="splash-subtitle">DIGITAL TWIN</div>
</div>
""", unsafe_allow_html=True)

# Create a placeholder that will be cleared once initialization finishes
loading_placeholder = st.empty()
loading_placeholder.markdown("""
<div class="skeleton-layer">
    <div class="skel-header">
        <div class="skel-box" style="width: 250px; height: 40px; border-radius: 20px;"></div>
    </div>
    <div class="skel-body">
        <div class="skel-col" style="width: 25%;">
            <div class="skel-box" style="width: 100%; height: 200px; margin-bottom: 20px;"></div>
            <div class="skel-box" style="width: 100%; height: 100px;"></div>
        </div>
        <div class="skel-col" style="width: 50%; padding: 0 20px;">
            <div class="skel-box" style="width: 70%; height: 120px; border-radius: 16px; margin-bottom: 24px;"></div>
            <div class="skel-box" style="width: 60%; height: 80px; border-radius: 16px; margin-bottom: 24px; margin-left: auto;"></div>
            <div class="skel-box" style="width: 100%; height: 60px; margin-top: auto; border-radius: 8px;"></div>
        </div>
        <div class="skel-col" style="width: 25%;">
            <div class="skel-box" style="width: 100%; height: 300px;"></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# Helper Functions

def _parse_sources_text(sources_text):
    """Parse the formatted sources string into a list of dicts for the right panel."""
    if not sources_text or "No sources found" in str(sources_text):
        return []

    parsed = []

    # Pattern: [1] "Title" (Year) — Type: ..., Relevance: ...
    pattern = r'\[(\d+)\]\s+"([^"]+)"\s+\(([^)]+)\)\s+—\s+Type:\s+([^,]+),\s+Relevance:\s+([\d.]+%)'

    for match in re.finditer(pattern, str(sources_text)):
        idx, title, year, src_type, relevance = match.groups()
        parsed.append({
            "index": int(idx),
            "title": title,
            "year": year,
            "source_type": src_type.strip(),
            "relevance_score": float(relevance.rstrip("%")) / 100,
            "chunk_text": "",
        })

    # If regex didn't match, try line-by-line fallback
    if not parsed and str(sources_text).strip():
        for i, line in enumerate(str(sources_text).strip().split("\n"), 1):
            line = line.strip()
            if line:
                parsed.append({
                    "index": i,
                    "title": line[:60],
                    "year": "",
                    "source_type": "",
                    "relevance_score": 0,
                    "chunk_text": line,
                })

    return parsed


# Session State Initialization

def get_agent_app():
    return build_graph()

agent_app = get_agent_app()

if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "ltm_store" not in st.session_state:
    st.session_state.ltm_store = LongTermMemoryStore()

# New UI state
if "timeline_mode" not in st.session_state:
    st.session_state.timeline_mode = "classic"

if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False

if "is_streaming" not in st.session_state:
    st.session_state.is_streaming = False

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []

if "last_trace" not in st.session_state:
    st.session_state.last_trace = []


# Initialization Complete - Clear Loading Screen
loading_placeholder.empty()

render_header()
render_mode_toggle()


# Three-Column Layout

left_col, chat_col, right_col = st.columns([2.4, 6.2, 2.4], gap="small")


# LEFT PANEL
with left_col:
    render_left_panel()


# CHAT COLUMN
with chat_col:
    # Inner container for max-width centering
    st.markdown('<div class="chat-column-inner">', unsafe_allow_html=True)

    # Determine era for message display
    mode = st.session_state.timeline_mode
    era = "1988" if mode == "classic" else ""

    # Map timeline mode to agent state format
    agent_mode = "Classic (1988)" if mode == "classic" else "Modern (Present Day)"

    # Show suggestions if conversation is empty
    if not st.session_state.messages:
        st.markdown("""<div style="text-align: center; margin: 60px 0 40px 0;">
<div style="font-family: 'Instrument Serif', serif; font-style: italic; font-size: 28px; color: var(--chalk-green); margin-bottom: 8px;">
Ask the Professor
</div>
<div style="font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--text-secondary); letter-spacing: 0.1em;">
PHYSICS &middot; LIFE &middot; CHALLENGER &middot; CURIOSITY
</div>
</div>""", unsafe_allow_html=True)
        render_suggestions()

    # We need a container for the chat history
    chat_history_container = st.container()
    
    with chat_history_container:
        # Display chat history
        for msg in st.session_state.messages:
            if isinstance(msg, HumanMessage):
                if isinstance(msg.content, list):
                    text = next((item["text"] for item in msg.content if item.get("type") == "text"), "")
                    img_url = next((item["image_url"]["url"] for item in msg.content if item.get("type") == "image_url"), None)
                    aud_url = next((item["audio_url"]["url"] for item in msg.content if item.get("type") == "audio_url"), None)
                    img_b64 = img_url.split(",")[1] if img_url else None
                    aud_b64 = aud_url.split(",")[1] if aud_url else None
                    
                    # Extract mime_type from url
                    mime_type = img_url.split(";")[0].split(":")[1] if img_url and ";" in img_url else "image/png"
                    
                    render_chat_message("user", text, image_b64=img_b64, audio_b64=aud_b64, mime_type=mime_type)
                else:
                    render_chat_message("user", msg.content)
            elif isinstance(msg, AIMessage):
                # Build source index list for citation chips
                source_chips = []
                for i, src in enumerate(st.session_state.last_sources):
                    source_chips.append({"index": i + 1})
                aud_b64 = msg.additional_kwargs.get("audio_b64")
                mime_type = msg.additional_kwargs.get("audio_mime_type", "audio/mp3")
                render_chat_message("feynman", msg.content, sources=source_chips, era=era, audio_b64=aud_b64, mime_type=mime_type)

    # Thinking placeholder
    thinking_placeholder = st.empty()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── INPUT ──
    import base64
    
    prompt_obj = st.chat_input(
        "Ask the Professor...",
        accept_file=True,
        file_type=["png", "jpg", "jpeg"],
        accept_audio=True
    )
    
    # Check if a suggestion was clicked
    if st.session_state.get("pending_suggestion"):
        # We simulate a text prompt object
        prompt_obj = {"text": st.session_state.pending_suggestion, "files": [], "audio": None}
        st.session_state.pending_suggestion = None
        
    if prompt_obj:
        text_input = prompt_obj["text"] if isinstance(prompt_obj, dict) and "text" in prompt_obj else getattr(prompt_obj, "text", "")
        files = prompt_obj["files"] if isinstance(prompt_obj, dict) and "files" in prompt_obj else getattr(prompt_obj, "files", [])
        audio = prompt_obj["audio"] if isinstance(prompt_obj, dict) and "audio" in prompt_obj else getattr(prompt_obj, "audio", None)
        
        # Append user message to state
        if files:
            uploaded_image = files[0]
            image_bytes = uploaded_image.getvalue()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            mime_type = uploaded_image.type
            
            # We no longer inject the default prompt into the UI state,
            # so the user doesn't see "What is shown in this image?"
            msg_content = [
                {"type": "text", "text": text_input},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
            ]
            st.session_state.messages.append(HumanMessage(content=msg_content))
            display_text = text_input
            with chat_history_container:
                render_chat_message("user", display_text, image_b64=base64_image, mime_type=mime_type)
        elif audio:
            audio_bytes = audio.getvalue()
            base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
            # For now we'll just show that audio was recorded
            msg_content = [
                {"type": "text", "text": text_input},
                {"type": "audio_url", "audio_url": {"url": f"data:audio/wav;base64,{base64_audio}"}}
            ]
            st.session_state.messages.append(HumanMessage(content=msg_content))
            display_text = text_input
            with chat_history_container:
                render_chat_message("user", display_text, audio_b64=base64_audio)
        else:
            st.session_state.messages.append(HumanMessage(content=text_input))
            display_text = text_input
            with chat_history_container:
                render_chat_message("user", display_text)
            
        with thinking_placeholder:
            render_thinking_bubble()

        # Set thinking state for Right Panel
        st.session_state.is_thinking = True
        st.session_state.last_trace = []
        st.session_state.last_sources = []

        try:
            # Prepare state for LangGraph
            initial_state = {
                "messages": st.session_state.messages.copy(),
                "session_id": st.session_state.session_id,
                "mode": agent_mode,
                "curiosity_mode": st.session_state.get("curiosity_mode", False),
                "feynman_technique": st.session_state.get("feynman_technique", False),
                "physics_depth": st.session_state.get("physics_depth", "I know the basics")
            }

            # Execute the agent
            final_state = agent_app.invoke(initial_state)

            # Get response and format
            raw_response = final_state["messages"][-1].content
            formatted_response = format_chat_message(raw_response)
            
            # Replace the last message content with the formatted string to prevent list/replace errors
            final_state["messages"][-1].content = formatted_response

            if audio:
                # Generate Voice
                import persona.voice
                importlib.reload(persona.voice)
                feynman_audio_b64 = persona.voice.generate_feynman_audio(formatted_response)
                if feynman_audio_b64:
                    final_state["messages"][-1].additional_kwargs["audio_b64"] = feynman_audio_b64
                    final_state["messages"][-1].additional_kwargs["audio_mime_type"] = "audio/mp3"
                else:
                    # Append a warning if it failed
                    final_state["messages"][-1].content += "\n\n*(ElevenLabs failed to generate audio. Check your console logs!)*"

            # Update messages
            st.session_state.messages = final_state["messages"]

            # Parse sources for right panel
            raw_sources = final_state.get("sources", "")
            parsed_sources = _parse_sources_text(raw_sources)
            st.session_state.last_sources = parsed_sources

            # Build trace for right panel
            st.session_state.last_trace = [
                {"name": "RAG Retrieval", "detail": f"Found {len(parsed_sources)} passages", "active": True},
                {"name": "Memory Lookup", "detail": "Session context added", "active": True},
                {"name": "Persona Response", "detail": "Complete", "active": True},
            ]

        except Exception as e:
            # If the API call fails, remove the user's message from history so it doesn't get stuck and bloat the payload
            if st.session_state.messages:
                st.session_state.messages.pop()
                
            error_msg = str(e)
            st.session_state.messages.append(
                AIMessage(content=f"API Error: {error_msg}")
            )
        finally:
            st.session_state.is_thinking = False
            st.session_state.is_streaming = False
            st.rerun()


# RIGHT PANEL
with right_col:
    render_right_panel()
