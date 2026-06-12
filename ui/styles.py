"""
UI Styles — All CSS injection for the Feynman Digital Twin.
Injects Google Fonts, CSS variables, global overrides, message
bubble styles, animations, panel styles, and responsive breakpoints.
"""

import streamlit as st


def inject_css():
    """Inject all custom CSS into the Streamlit app."""

    # Google Fonts
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Mono:wght@400;500&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    # Full CSS injection
    st.markdown("""
    <style>
    /*
       CSS VARIABLES — Colour System
    */
    :root {
        --bg-primary:    #0F0E0B;
        --bg-surface:    #161410;
        --bg-elevated:   #1E1B16;
        --bg-chalk:      #F5F0E8;
        --chalk-green:   #7CAE8E;
        --chalk-green-dim: #4A7A5E;
        --amber-light:   #D4A547;
        --amber-dim:     #8A6A2E;
        --text-primary:  #EDE8DC;
        --text-secondary: #9A9181;
        --text-feynman:  #1A1710;
        --text-user:     #EDE8DC;
        --rule-color:    #2E2A22;
        --cite-bg:       #2A2318;
    }

    /* 
       GLOBAL RESETS
    */
    body, .stApp {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Lora', serif !important;
    }

    /* Hide Streamlit default chrome */
    #MainMenu, header, footer, .stDeployButton { visibility: hidden !important; }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* Kill Streamlit's blue decoration ribbon */
    [data-testid="stDecoration"],
    .stDecoration {
        display: none !important;
        background: none !important;
        background-image: none !important;
    }

    /* Kill stApp pseudo-element decorations (blue edge glow) */
    .stApp::before, .stApp::after {
        display: none !important;
        background: none !important;
        background-image: none !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* Kill any remaining blue focus rings on Streamlit inputs */
    *:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    input:focus, textarea:focus, select:focus, button:focus {
        border-color: var(--chalk-green-dim) !important;
        box-shadow: none !important;
        outline: none !important;
    }

    /* Override column padding */
    [data-testid="column"] { padding: 0 !important; }

    /* Hide sidebar completely */
    [data-testid="stSidebar"] { display: none !important; }
    .stSidebar { display: none !important; }

    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--rule-color); border-radius: 2px; }

    /*
       HEADER BAR
    */
    .feynman-header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px 24px;
        border-bottom: 1px solid var(--rule-color);
        background: var(--bg-surface);
        position: sticky;
        top: 0;
        z-index: 100;
    }

    /* Feynman portrait */
    .feynman-portrait {
        width: 52px; height: 52px;
        border-radius: 50%;
        object-fit: cover;
        border: 1.5px solid var(--chalk-green-dim);
        filter: grayscale(1) contrast(1.15) brightness(0.9);
        transition: filter 0.3s ease;
    }

    /* Portrait fallback */
    .portrait-fallback {
        width: 52px; height: 52px;
        border-radius: 50%;
        border: 1.5px solid var(--chalk-green-dim);
        background: var(--bg-elevated);
        display: flex; align-items: center; justify-content: center;
        font-family: 'Instrument Serif', serif;
        font-size: 18px;
        color: var(--chalk-green);
        font-style: italic;
    }

    /* Thinking animation */
    @keyframes feynman-think {
        0%, 100% { filter: grayscale(1) contrast(1.05) brightness(0.85); transform: rotate(-0.4deg); }
        50%       { filter: grayscale(1) contrast(1.3) brightness(0.98); transform: rotate(0.4deg); }
    }
    .feynman-thinking .feynman-portrait {
        animation: feynman-think 1.2s ease-in-out infinite;
    }

    /* Speaking animation */
    @keyframes feynman-speak {
        0%   { filter: grayscale(0.6) contrast(1.2) brightness(1.0); }
        100% { filter: grayscale(1.0) contrast(1.0) brightness(0.88); }
    }
    .feynman-speaking .feynman-portrait {
        animation: feynman-speak 0.7s ease-in-out infinite alternate;
    }

    /* Mode toggle pills */
    .mode-pill {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        padding: 5px 12px;
        border-radius: 20px;
        cursor: pointer;
        border: 1px solid var(--rule-color);
        color: var(--text-secondary);
        background: transparent;
        transition: all 0.15s;
        text-decoration: none;
        display: inline-block;
    }
    .mode-pill.active {
        border-color: var(--chalk-green-dim);
        color: var(--chalk-green);
        background: rgba(74, 122, 94, 0.1);
    }
    .mode-pill:hover {
        border-color: var(--chalk-green-dim);
        color: var(--chalk-green);
    }

    /* Status indicator */
    @keyframes pulse-green {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    .status-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    .status-dot.idle { background: var(--text-secondary); }
    .status-dot.thinking { background: var(--chalk-green); animation: pulse-green 1s infinite; }
    .status-dot.streaming { background: var(--amber-light); animation: pulse-green 0.5s infinite; }

    /* 
       MESSAGE BUBBLES
    */

    /* Feynman message (left-aligned, cream) */
    .msg-feynman {
        background: var(--bg-chalk);
        border-radius: 2px 12px 12px 12px;
        padding: 16px 18px;
        margin: 0 auto 20px 0;
        max-width: 85%;
        box-shadow: 0 2px 16px rgba(0,0,0,0.35);
        font-family: 'Lora', serif;
        font-size: 15px;
        line-height: 1.75;
        color: var(--text-feynman);
    }

    /* User message (right-aligned, dark) */
    .msg-user {
        background: var(--bg-elevated);
        border: 1px solid var(--rule-color);
        border-radius: 12px 12px 2px 12px;
        padding: 12px 16px;
        margin: 0 0 20px auto;
        max-width: 72%;
        font-family: 'Lora', serif;
        font-size: 15px;
        line-height: 1.7;
        color: var(--text-primary);
    }

    /* Thinking dots */
    @keyframes dot-bounce {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-5px); }
    }
    .thinking-dot {
        display: inline-block;
        width: 6px; height: 6px;
        background: var(--chalk-green-dim);
        border-radius: 50%;
        margin: 0 3px;
    }
    .thinking-dot:nth-child(1) { animation: dot-bounce 1s 0.0s infinite; }
    .thinking-dot:nth-child(2) { animation: dot-bounce 1s 0.15s infinite; }
    .thinking-dot:nth-child(3) { animation: dot-bounce 1s 0.3s infinite; }

    /* Citation chip */
    .msg-feynman span.cite-chip, .cite-chip {
        display: inline-block;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        color: var(--bg-chalk) !important;
        background: var(--cite-bg);
        border: 1px solid var(--amber-dim);
        padding: 1px 5px;
        border-radius: 3px;
        margin: 0 2px;
        cursor: pointer;
    }

    /*  
       SPLASH SCREEN & SKELETON
    */
    @keyframes splashFade {
        0% { opacity: 1; }
        80% { opacity: 1; }
        100% { opacity: 0; visibility: hidden; pointer-events: none; }
    }
    @keyframes skeletonFade {
        0% { opacity: 1; }
        80% { opacity: 1; }
        100% { opacity: 0; visibility: hidden; pointer-events: none; }
    }
    @keyframes pulse-skeleton {
        0% { opacity: 0.2; }
        100% { opacity: 0.6; }
    }

    /* Phase 1: Portrait Splash (0-2s) */
    .splash-screen {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: var(--bg-primary);
        z-index: 99999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        animation: splashFade 2.0s cubic-bezier(0.8, 0, 0.2, 1) forwards;
    }
    .splash-portrait {
        width: 120px; height: 120px;
        border-radius: 50%;
        margin-bottom: 24px;
        filter: grayscale(1) contrast(1.1);
        opacity: 0.9;
        box-shadow: 0 0 40px rgba(124, 174, 142, 0.1);
    }
    .splash-title {
        font-family: 'Instrument Serif', serif;
        font-size: 36px;
        color: var(--chalk-green);
        font-style: italic;
        margin-bottom: 8px;
    }
    .splash-subtitle {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        color: var(--text-secondary);
        letter-spacing: 0.25em;
    }

    /* Phase 2: Skeleton Loader (Persistent until loaded) */
    .skeleton-layer {
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: var(--bg-primary);
        z-index: 99998;
        display: flex;
        flex-direction: column;
        padding: 24px;
        box-sizing: border-box;
    }
    .skel-header {
        height: 80px; width: 100%;
        display: flex; align-items: center; justify-content: center;
        border-bottom: 1px solid var(--rule-color);
        margin-bottom: 24px;
    }
    .skel-body {
        flex: 1; display: flex; gap: 24px;
        width: 100%;
    }
    .skel-col {
        display: flex; flex-direction: column;
    }
    .skel-box {
        background: rgba(124, 174, 142, 0.15); /* Chalk green tint */
        border: 1px dashed var(--chalk-green-dim);
        border-radius: 4px;
        animation: pulse-skeleton 1.5s infinite alternate;
    }

    /*  
       LEFT PANEL — Memory & Context
    */

    .panel-top-decor {
        font-family: 'Instrument Serif', serif;
        font-size: 14px;
        color: var(--text-secondary);
        border-bottom: 1px solid rgba(46, 42, 34, 0.5);
        padding-bottom: 16px;
        margin-bottom: 24px;
        text-align: center;
        opacity: 0.7;
    }
    .panel-top-decor .university {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 9px;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .panel-top-decor .sketch {
        font-family: 'Lora', serif;
        font-style: italic;
        font-size: 16px;
        margin-top: 10px;
        color: var(--chalk-green-dim);
    }

    .panel-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        color: var(--text-secondary);
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid var(--rule-color);
    }

    .memory-card {
        background: var(--bg-elevated);
        border-left: 2px solid var(--chalk-green-dim);
        padding: 8px 10px;
        margin-bottom: 6px;
        border-radius: 0 4px 4px 0;
    }
    .memory-card .mem-text {
        font-family: 'Lora', serif;
        font-size: 13px;
        color: var(--text-primary);
        line-height: 1.4;
    }
    .memory-card .mem-meta {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        color: var(--text-secondary);
        margin-top: 3px;
    }

    .memory-empty {
        font-family: 'Lora', serif;
        font-style: italic;
        font-size: 12px;
        color: var(--text-secondary);
        line-height: 1.6;
        padding: 12px 10px;
        background: rgba(30, 27, 22, 0.4);
        border: 1px dashed var(--rule-color);
        border-radius: 4px;
        margin-top: 4px;
        text-align: center;
    }

    .chalk-sketch {
        font-size: 24px;
        color: var(--rule-color);
        margin-bottom: 8px;
        text-align: center;
        opacity: 0.7;
    }

    /* User interest tags */
    .interest-tag {
        display: inline-block;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        background: var(--cite-bg);
        color: var(--amber-light);
        border: 1px solid var(--amber-dim);
        padding: 2px 6px;
        border-radius: 3px;
        margin: 2px 3px 2px 0;
    }

    /*  
       RIGHT PANEL — Reasoning & Sources
    */

    .node-trace {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        margin-bottom: 10px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
    }
    .node-dot-active {
        width: 8px; height: 8px; border-radius: 50%;
        background: var(--chalk-green); margin-top: 2px; flex-shrink: 0;
    }
    .node-dot-inactive {
        width: 8px; height: 8px; border-radius: 50%;
        border: 1px solid var(--text-secondary); margin-top: 2px; flex-shrink: 0;
    }
    .node-label {
        color: var(--text-primary);
        font-size: 11px;
    }
    .node-detail {
        color: var(--text-secondary);
        font-size: 10px;
        margin-top: 1px;
    }
    .node-connector {
        width: 1px;
        height: 8px;
        border-left: 1px dashed var(--rule-color);
        margin-left: 3.5px;
        margin-bottom: 2px;
    }

    /* Source card */
    .source-card {
        background: var(--bg-elevated);
        border: 1px solid var(--rule-color);
        border-radius: 4px;
        padding: 8px 10px;
        margin-bottom: 8px;
        cursor: pointer;
        transition: border-color 0.15s;
    }
    .source-card:hover { border-color: var(--amber-dim); }
    .source-num {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        color: var(--amber-light);
        background: var(--cite-bg);
        padding: 1px 4px;
        border-radius: 2px;
        margin-right: 6px;
    }
    .source-title {
        font-family: 'Lora', serif;
        font-size: 12px;
        color: var(--text-primary);
    }
    .source-meta {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        color: var(--text-secondary);
        margin-top: 2px;
    }
    .source-preview {
        font-family: 'Lora', serif;
        font-style: italic;
        font-size: 11px;
        color: var(--text-secondary);
        margin-top: 4px;
        line-height: 1.4;
    }
    .source-expanded {
        border-left: 2px solid var(--amber-dim);
        padding: 8px 10px;
        margin-top: 6px;
        font-family: 'Lora', serif;
        font-size: 12px;
        color: var(--text-primary);
        line-height: 1.6;
        background: var(--bg-surface);
        border-radius: 0 4px 4px 0;
    }

    /*  
       INPUT OVERRIDES
    */
    .stChatInput {
        background: transparent !important;
    }
    .stChatInput > div {
        background: var(--bg-elevated) !important;
        border: 1px solid var(--rule-color) !important;
        border-radius: 8px !important;
    }
    .stChatInput textarea {
        background: transparent !important;
        border: none !important;
        color: var(--text-primary) !important;
        font-family: 'Lora', serif !important;
        font-size: 15px !important;
    }
    .stChatInput textarea:focus {
        border-color: var(--chalk-green-dim) !important;
        outline: none !important;
        box-shadow: none !important;
    }
    .stChatInput textarea::placeholder {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 13px !important;
        color: var(--text-secondary) !important;
    }
    .stChatInput button {
        background: transparent !important;
        border: none !important;
        color: var(--chalk-green) !important;
        font-family: 'IBM Plex Mono', monospace !important;
    }
    .stChatInput button:hover {
        color: var(--chalk-green-dim) !important;
    }

    /* Suggestion chips (now handled by general button styling) */
    
    /*  
       PANEL CONTAINERS
    */
    [data-testid="column"]:has(#left-panel-marker) {
        padding: 16px 14px !important;
        height: calc(100vh - 82px);
        overflow-y: auto;
        border-right: 1px solid var(--rule-color);
        background: var(--bg-surface);
    }
    [data-testid="column"]:has(#right-panel-marker) {
        padding: 16px 14px !important;
        height: calc(100vh - 82px);
        overflow-y: auto;
        border-left: 1px solid var(--rule-color);
        background: var(--bg-surface);
    }
    .chat-column-inner {
        max-width: 680px;
        margin: 0 auto;
        padding: 24px 16px 100px 16px;
    }

    /* 
       STREAMLIT OVERRIDES
    */

    /* Override button styles used for mode toggle and suggestion chips */
    .stButton > button {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        padding: 5px 12px !important;
        border-radius: 20px !important;
        transition: all 0.15s !important;
        line-height: 1.4 !important;
    }
    .stButton > button[kind="primary"] {
        border: 1px solid var(--chalk-green-dim) !important;
        color: var(--chalk-green) !important;
        background: rgba(74, 122, 94, 0.1) !important;
    }
    .stButton > button[kind="secondary"] {
        border: 1px solid var(--rule-color) !important;
        color: var(--text-secondary) !important;
        background: transparent !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: var(--chalk-green-dim) !important;
        color: var(--chalk-green) !important;
    }
    .stButton > button:focus {
        box-shadow: none !important;
        outline: none !important;
    }

    /* Expander styling for source details */
    .streamlit-expanderHeader {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        color: var(--text-secondary) !important;
        background: var(--bg-elevated) !important;
        border: 1px solid var(--rule-color) !important;
        border-radius: 4px !important;
    }
    .streamlit-expanderContent {
        background: var(--bg-surface) !important;
        border: 1px solid var(--rule-color) !important;
        border-top: none !important;
    }

    /* 
       RESPONSIVE BREAKPOINTS
    */
    @media (max-width: 1100px) {
        [data-testid="column"]:has(#left-panel-marker) { display: none !important; }
    }
    @media (max-width: 800px) {
        [data-testid="column"]:has(#right-panel-marker) { display: none !important; }
        .chat-column-inner { max-width: 100%; padding: 16px 10px 100px 10px; }
    }

    /* Override Streamlit's default stMarkdown text color */
    .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: var(--text-primary) !important;
    }
    
    /* Ensure Feynman's text stays dark on the cream bubble */
    .msg-feynman, .msg-feynman p, .msg-feynman span, .msg-feynman div {
        color: var(--text-feynman) !important;
    }

    /* Override horizontal rule color */
    hr { border-color: var(--rule-color) !important; }

    </style>
    """, unsafe_allow_html=True)
