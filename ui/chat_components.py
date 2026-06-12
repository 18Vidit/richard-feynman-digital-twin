"""
UI Chat Column — Message rendering and input. 
Renders the central chat area with custom message bubbles,
thinking indicator, and suggestion chips.
"""

import re
import streamlit as st


def render_chat_message(role: str, content: str, sources: list = None, era: str = "1988", image_b64: str = None, audio_b64: str = None, mime_type: str = "image/png"):
    """
    Render a single chat message with custom styling.
    
    Args:
        role: "user" or "feynman"
        content: The message text
        sources: List of source dicts with keys: index, title, year
        era: "1988" for classic mode, "" for modern mode
        image_b64: Optional base64 string of an uploaded image
        audio_b64: Optional base64 string of an audio message
        mime_type: MIME type of the image
    """
    if role == "user":
        # Make sure content has at least a space to avoid completely empty blocks
        safe_content = _sanitize_html(content) if content else "&nbsp;"
        img_html = f'<img src="data:{mime_type};base64,{image_b64}" style="max-width: 100%; border-radius: 8px; margin-top: 8px;" />' if image_b64 else ""
        audio_html = f'<audio controls src="data:audio/wav;base64,{audio_b64}" style="margin-top: 8px;"></audio>' if audio_b64 else ""
        
        st.html(f"""<div style="display: flex; flex-direction: column; align-items: flex-end; margin-bottom: 20px;">
<div class="msg-user">
    {safe_content}
    {img_html}
    {audio_html}
</div>
<div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--text-secondary); margin-top: 4px; margin-right: 4px;">
You
</div>
</div>""")
    
    elif role == "feynman":
        # Process content: convert markdown bold to italic (per design spec)
        # Ensure content is a string
        if isinstance(content, list):
            blocks = []
            for block in content:
                if isinstance(block, dict) and "text" in block:
                    blocks.append(block["text"])
                elif isinstance(block, str):
                    blocks.append(block)
            content = "".join(blocks)
        # Check for python_feynman blocks
        feynman_code_blocks = re.findall(r'```python_feynman(.*?)```', str(content), re.DOTALL)
        
        # Strip the code blocks from the content so they don't show up in the text bubble
        display_content = re.sub(r'```python_feynman.*?```', '', str(content), flags=re.DOTALL)
        
        processed = _process_feynman_text(display_content)
        
        # Build citation chips HTML
        cite_chips = ""
        if sources:
            for s in sources:
                idx = s.get("index", s.get("i", ""))
                cite_chips += f'<span class="cite-chip">[{idx}]</span> '
        
        # Era label
        era_label = "&mdash; Feynman"
        
        # Citation footer (only if we have citations or era)
        footer_html = ""
        if cite_chips or era:
            footer_html = f"""<div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(26,23,16,0.12); display: flex; justify-content: space-between; align-items: center;">
<div>{cite_chips}</div>
<div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--amber-dim); font-style: italic;">
{era_label}
</div>
</div>"""
        
        st.html(f"""<div style="display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 8px;">
<div class="msg-feynman">
{processed}
{footer_html}
</div>
</div>""")

        # Execute and render any feynman diagrams
        import os
        for code in feynman_code_blocks:
            try:
                namespace = {}
                exec(code.strip(), namespace)
                if os.path.exists('feynman_temp.png'):
                    st.image('feynman_temp.png', caption="Feynman Diagram", width=400)
                    os.remove('feynman_temp.png')
            except Exception as e:
                st.error(f"Failed to render diagram: {e}")

        if audio_b64:
            import base64
            st.audio(base64.b64decode(audio_b64), format=mime_type if "audio" in mime_type else "audio/mp3", autoplay=True)


def render_thinking_bubble():
    """Show the animated thinking indicator (three bouncing dots in a cream bubble)."""
    st.html("""<div style="display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 24px;">
<div class="msg-feynman" style="padding: 16px 24px;">
<span class="thinking-dot"></span>
<span class="thinking-dot"></span>
<span class="thinking-dot"></span>
</div>
</div>""")


def render_suggestions():
    """Render suggestion chips when the conversation is empty."""
    suggestions = [
        "What is a photon, really?",
        "Explain QED simply",
        "Tell me about the Manhattan Project",
        "How do atoms work?",
        "What is the path integral?",
    ]
    
    # We use columns to simulate inline buttons
    cols = st.columns(len(suggestions))
    for i, s in enumerate(suggestions):
        with cols[i]:
            if st.button(s, key=f"sug_{i}", type="secondary", use_container_width=True):
                st.session_state.pending_suggestion = s
                st.rerun()


def _sanitize_html(text: str) -> str:
    """Basic HTML escaping for user text."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    # Preserve newlines as <br>
    text = text.replace("\n", "<br>")
    return text


def _process_feynman_text(text: str) -> str:
    """
    Process Feynman's response text for display.
    
    - Converts **bold** to <em> (italic) per design spec
    - Converts [Source N] to citation chip HTML  
    - Preserves paragraph breaks
    """
    # Convert markdown bold to italic (design says no bold, use italic for emphasis)
    text = re.sub(r'\*\*(.+?)\*\*', r'<em>\1</em>', text)
    
    # Convert single asterisk italic
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    
    # Convert [Source N] references to citation chips
    text = re.sub(
        r'\[Source (\d+)\]',
        r'<span class="cite-chip">[\1]</span>',
        text,
        flags=re.IGNORECASE
    )
    
    # Convert (Source N) references to citation chips
    text = re.sub(
        r'\(Source (\d+)\)',
        r'<span class="cite-chip">[\1]</span>',
        text,
        flags=re.IGNORECASE
    )
    
    # Strip any leading "Feynman:" type prefixes
    prefixes = ["Richard Feynman: ", "Feynman: ", "Me: ", "I think: "]
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
    
    # Preserve paragraph breaks
    text = text.replace("\n\n", "</p><p>")
    text = text.replace("\n", "<br>")
    text = f"<p>{text}</p>"
    
    return text
