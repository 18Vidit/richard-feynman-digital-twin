"""
UI Right Panel — Reasoning Trace & Sources.
Renders the sticky right column showing the agent's
node execution trace and retrieved source cards.
"""

import streamlit as st


def render_right_panel():
    """Render the right panel with reasoning trace and source cards."""
    # Right Panel content
    st.markdown('<div id="right-panel-marker"></div>', unsafe_allow_html=True)
    
    st.markdown("""<div class="panel-top-decor">
<div style="font-family: 'IBM Plex Mono', monospace; line-height: 1.1; margin-bottom: 16px; color: var(--chalk-green-dim); opacity: 0.8; font-size: 10px; text-align: center;">
  e&minus; &searr; &nbsp; &nbsp; &nearr; e&minus;<br>
&nbsp; &nbsp; &bull;&mdash;&sim;&sim;&mdash;&bull; &nbsp; <br>
  e+ &nearr; &nbsp; &nbsp; &searr; e+
</div>
<div class="university">Physics 201</div>
Quantum Electrodynamics
</div>""", unsafe_allow_html=True)
    
    # Section: His Reasoning
    st.markdown('<div class="panel-label">His Reasoning</div>', unsafe_allow_html=True)
    
    trace = st.session_state.get("last_trace", [])
    is_thinking = st.session_state.get("is_thinking", False)
    
    if is_thinking:
        # Show active trace during generation
        _render_trace_item("RAG Retrieval", "Searching knowledge base...", active=True)
        _render_connector()
        _render_trace_item("Memory Lookup", "Checking session context...", active=False)
        _render_connector()
        _render_trace_item("Persona Response", "Generating...", active=False)
    elif trace:
        for i, node in enumerate(trace):
            _render_trace_item(
                node.get("name", "Node"),
                node.get("detail", ""),
                active=node.get("active", True)
            )
            if i < len(trace) - 1:
                _render_connector()
    else:
        st.markdown("""<div class="memory-empty">
<div class="chalk-sketch" style="font-size: 16px; margin-bottom: 8px;">&#8866;&#8867;</div>
Ask a question to see<br>
his thought process.
</div>""", unsafe_allow_html=True)
    
    # Section: Sources Consulted 
    st.markdown(
        '<div class="panel-label" style="margin-top: 24px;">Sources Consulted</div>',
        unsafe_allow_html=True
    )
    
    sources = st.session_state.get("last_sources", [])
    
    if sources:
        for i, src in enumerate(sources):
            _render_source_card(i + 1, src)
    else:
        st.markdown("""<div class="memory-empty">
<div class="chalk-sketch" style="font-size: 16px; margin-bottom: 8px;">&#9823;</div>
Sources will appear here<br>
after each response.
</div>""", unsafe_allow_html=True)
    
    # End of Right Panel


def _render_trace_item(name: str, detail: str, active: bool = True):
    """Render a single node trace item."""
    dot_class = "node-dot-active" if active else "node-dot-inactive"
    
    st.markdown(f"""<div class="node-trace">
<div class="{dot_class}"></div>
<div>
<div class="node-label">{name}</div>
<div class="node-detail">{detail}</div>
</div>
</div>""", unsafe_allow_html=True)


def _render_connector():
    """Render the dashed connector line between trace nodes."""
    st.markdown('<div class="node-connector"></div>', unsafe_allow_html=True)


def _render_source_card(index: int, source: dict):
    """Render a single source card with collapsible detail."""
    title = source.get("title", "Unknown Source")
    year = source.get("year", "")
    source_type = source.get("source_type", "")
    relevance = source.get("relevance_score", 0)
    chunk_text = source.get("chunk_text", "")
    
    # Truncated preview
    preview = ""
    if chunk_text:
        preview = chunk_text[:80].strip()
        if len(chunk_text) > 80:
            preview += "..."
    
    # Build metadata line
    meta_parts = []
    if source_type:
        meta_parts.append(source_type.replace("_", " ").title())
    if year:
        meta_parts.append(str(year))
    if relevance:
        meta_parts.append(f"{relevance:.0%} match")
    meta_line = " &middot; ".join(meta_parts)
    
    # Use Streamlit expander for collapsible behavior
    with st.expander(f"[{index}]  {title}", expanded=False):
        if meta_line:
            st.markdown(f"""<div class="source-meta">{meta_line}</div>""", unsafe_allow_html=True)
        if preview:
            st.markdown(f"""<div class="source-preview">&ldquo;{preview}&rdquo;</div>""", unsafe_allow_html=True)
        if chunk_text and len(chunk_text) > 80:
            st.markdown(f"""<div class="source-expanded">{chunk_text}</div>""", unsafe_allow_html=True)
