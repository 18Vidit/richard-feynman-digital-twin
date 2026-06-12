"""
UI Left Panel — Memory & Context display.
Renders the sticky left column showing user memories
and inferred interest tags.
"""

import streamlit as st
import datetime


def render_left_panel():
    """Render the left panel with memory log and user profile."""
    # Left Panel content
    st.markdown('<div id="left-panel-marker"></div>', unsafe_allow_html=True)
    
    st.markdown("""<div class="panel-top-decor">
<img src="https://upload.wikimedia.org/wikipedia/commons/1/1a/RichardFeynman-PaineMansionWoods1984_copyrightTamikoThiel_bw.jpg" style="width: 100%; border-radius: 4px; margin-bottom: 16px; filter: grayscale(1) contrast(1.1) brightness(0.85); opacity: 0.9;" />
<div class="university">California Institute of Technology</div>
Pasadena, California
<div class="sketch">&int; e<sup>ix</sup> dx</div>
</div>""", unsafe_allow_html=True)
    
    # Section: Teaching Style
    st.markdown('<div class="panel-label">Teaching Style</div>', unsafe_allow_html=True)
    
    # Curiosity Mode toggle
    if "curiosity_mode" not in st.session_state:
        st.session_state.curiosity_mode = False
        
    curiosity = st.toggle("Socratic Mode (Ask Questions)", value=st.session_state.curiosity_mode)
    if curiosity != st.session_state.curiosity_mode:
        st.session_state.curiosity_mode = curiosity
        st.rerun()
        
    # Feynman Technique toggle
    if "feynman_technique" not in st.session_state:
        st.session_state.feynman_technique = False
        
    feynman_tech = st.toggle("Feynman Technique Mode", value=st.session_state.feynman_technique)
    if feynman_tech != st.session_state.feynman_technique:
        st.session_state.feynman_technique = feynman_tech
        st.rerun()
        
    # Audience Depth Selector
    if "physics_depth" not in st.session_state:
        st.session_state.physics_depth = "I know the basics"
        
    st.markdown('<div style="margin-bottom: 8px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 4px;">Physics Depth</div>', unsafe_allow_html=True)
    depth_options = ["Like I'm new", "I know the basics", "Peer"]
    selected_depth = st.selectbox(
        "Physics Depth", 
        options=depth_options, 
        index=depth_options.index(st.session_state.physics_depth),
        label_visibility="collapsed"
    )
    if selected_depth != st.session_state.physics_depth:
        st.session_state.physics_depth = selected_depth
        st.rerun()

    if st.session_state.curiosity_mode:
        st.markdown("""<div style="font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--chalk-green); margin-bottom: 12px; margin-top: 12px; padding: 8px; border: 1px dashed var(--chalk-green-dim); border-radius: 4px; background: rgba(124, 174, 142, 0.05);">
        &#9881; Feynman will now guide you with questions instead of giving direct answers.
        </div>""", unsafe_allow_html=True)
    elif st.session_state.feynman_technique:
        st.markdown("""<div style="font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--chalk-green); margin-bottom: 12px; margin-top: 12px; padding: 8px; border: 1px dashed var(--chalk-green-dim); border-radius: 4px; background: rgba(124, 174, 142, 0.05);">
        &#9881; You explain it! Feynman will probe your explanation for weaknesses.
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="margin-bottom: 12px;"></div>', unsafe_allow_html=True)
        
    if st.button("📖 Tell me a story!", use_container_width=True):
        st.session_state.pending_suggestion = "Tell me an interesting anecdote or story from your life related to our conversation, or just something you find fascinating."
        st.rerun()
        
    st.markdown('<div style="margin-bottom: 24px;"></div>', unsafe_allow_html=True)
    
    # Section: In His Memory 
    st.markdown('<div class="panel-label">In His Memory</div>', unsafe_allow_html=True)
    
    # Get memories from the store
    ltm_store = st.session_state.get("ltm_store")
    memories = []
    if ltm_store:
        try:
            memories = ltm_store.get_memories(
                st.session_state.get("session_id"), limit=10
            )
        except Exception:
            memories = []
    
    if memories:
        for mem in memories:
            content = mem.get("content", "")
            timestamp = mem.get("timestamp", "")
            
            # Format relative time
            time_label = _format_relative_time(timestamp)
            session_label = f"Session {mem.get('session_id', '')[:6]}"
            
            st.markdown(f"""<div class="memory-card">
<div class="mem-text">&darr; {content}</div>
<div class="mem-meta">{session_label} &middot; {time_label}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="memory-empty">
<div class="chalk-sketch" style="font-size: 14px; margin-bottom: 12px; font-style: normal; opacity: 0.6;">
"I would rather have questions that can't be answered than answers that can't be questioned."
</div>
No memory yet.<br>
Talk to him &mdash; he remembers<br>
what matters.
</div>""", unsafe_allow_html=True)
    
    # Section: You 
    st.markdown(
        '<div class="panel-label" style="margin-top: 24px;">You</div>',
        unsafe_allow_html=True
    )
    
    # Extract interest tags from memories
    tags = _extract_interest_tags(memories)
    
    if tags:
        tags_html = ""
        for tag in tags:
            tags_html += f'<span class="interest-tag">{tag}</span>'
        st.markdown(tags_html, unsafe_allow_html=True)
    else:
        st.markdown("""<div class="memory-empty">
Your interests will appear<br>
here as you chat.
</div>""", unsafe_allow_html=True)
    
    # End of Left Panel


def _format_relative_time(timestamp_str: str) -> str:
    """Convert an ISO timestamp to a relative time string."""
    if not timestamp_str:
        return "just now"
    
    try:
        ts = datetime.datetime.fromisoformat(timestamp_str)
        now = datetime.datetime.now(datetime.timezone.utc)
        
        # Make ts timezone-aware if it isn't
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=datetime.timezone.utc)
        
        diff = now - ts
        minutes = int(diff.total_seconds() / 60)
        
        if minutes < 1:
            return "just now"
        elif minutes < 60:
            return f"{minutes} min ago"
        elif minutes < 1440:
            hours = minutes // 60
            return f"{hours}h ago"
        else:
            days = minutes // 1440
            return f"{days}d ago"
    except (ValueError, TypeError):
        return "recently"


def _extract_interest_tags(memories: list) -> list:
    """Extract unique interest/topic tags from memories."""
    tags = set()
    
    # Extract from memory types
    for mem in memories:
        mem_type = mem.get("memory_type", "").lower()
        if mem_type and mem_type not in ("general", "unknown", ""):
            tags.add(mem_type)
    
    # Extract some common physics keywords from content
    physics_keywords = [
        "physics", "quantum", "QED", "electrodynamics", "atoms",
        "particles", "energy", "light", "photon", "gravity",
        "mechanics", "relativity", "Challenger", "teaching",
        "mathematics", "science", "experiment", "theory",
    ]
    
    for mem in memories:
        content = mem.get("content", "").lower()
        for kw in physics_keywords:
            if kw.lower() in content:
                tags.add(kw.lower())
    
    return sorted(list(tags))[:8]  # Max 8 tags
