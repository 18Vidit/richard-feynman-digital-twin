"""
UI Header — Feynman Digital Twin header bar.
Renders the full-width sticky header with Feynman portrait,
identity block, timeline mode toggle, and status indicator.
"""

import streamlit as st


# Feynman portrait URL (public domain, Wikimedia Commons)
FEYNMAN_PORTRAIT_URL = (
    "https://upload.wikimedia.org/wikipedia/en/4/42/Richard_Feynman_Nobel.jpg"
)


def render_header():
    """Render the full-width header bar above the columns."""
    
    # Determine animation state
    thinking = st.session_state.get("is_thinking", False)
    speaking = st.session_state.get("is_streaming", False)
    
    state_class = "feynman-thinking" if thinking else ("feynman-speaking" if speaking else "")
    status_class = "thinking" if thinking else ("streaming" if speaking else "idle")
    status_text = "Reasoning..." if thinking else ("Speaking..." if speaking else "Waiting")
    
    # Timeline mode
    mode = st.session_state.get("timeline_mode", "classic")
    classic_active = "active" if mode == "classic" else ""
    modern_active = "active" if mode == "modern" else ""
    
    # Render header HTML
    st.markdown(f"""
    <div class="feynman-header {state_class}">
        <div>
            <img class="feynman-portrait" 
                 src="{FEYNMAN_PORTRAIT_URL}"
                 width="52" height="52"
                 onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
                 alt="Richard Feynman" />
            <div class="portrait-fallback" style="display:none;">RPF</div>
        </div>
        <div>
            <div style="font-family: 'Instrument Serif', serif; font-style: italic; 
                        font-size: 20px; color: var(--chalk-green); line-height: 1.1;">
                Richard P. Feynman
            </div>
            <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px; 
                        color: var(--text-secondary); letter-spacing: 0.12em; margin-top: 2px;">
                NOBEL LAUREATE &middot; CALTECH
            </div>
        </div>
        <div style="flex: 1;"></div>
        <div style="display: flex; gap: 6px; align-items: center; margin-right: 16px;"
             id="mode-toggle-placeholder">
        </div>
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 11px; 
                    color: var(--text-secondary); display: flex; align-items: center;">
            <span class="status-dot {status_class}"></span>
            {status_text}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_mode_toggle():
    """Render the timeline mode toggle as Streamlit buttons.
    
    Call this after render_header() — it places the toggle buttons
    using st.columns inside the header area.
    """
    mode = st.session_state.get("timeline_mode", "classic")
    
    # Use small columns for the toggle
    cols = st.columns([6, 1.2, 1.5, 6])
    
    with cols[1]:
        if st.button(
            "Classic — 1988",
            key="mode_classic",
            type="primary" if mode == "classic" else "secondary",
            use_container_width=True
        ):
            st.session_state.timeline_mode = "classic"
            st.rerun()
    
    with cols[2]:
        if st.button(
            "Modern — Present",
            key="mode_modern",
            type="primary" if mode == "modern" else "secondary",
            use_container_width=True
        ):
            st.session_state.timeline_mode = "modern"
            st.rerun()
