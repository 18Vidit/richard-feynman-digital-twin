"""
Persona Formatter — Utilities for formatting Feynman's responses.
This module contains helpers for taking the raw output from the RAG chain
and formatting it nicely for the user interface, including parsing
implicit citations and adding Feynman-esque visual flair.
"""

import re


def format_chat_message(raw_text: str) -> str:
    """
    Format the raw LLM response.
    
    This can be used to:
    1. Clean up stray markdown artifacts
    2. Stylize citations
    3. Add a conversational prefix if missing
    """
    # The LangChain Gemini integration sometimes returns content as a list of dict blocks
    if isinstance(raw_text, list):
        blocks = []
        for block in raw_text:
            if isinstance(block, dict) and "text" in block:
                blocks.append(block["text"])
            elif isinstance(block, str):
                blocks.append(block)
        raw_text = "".join(blocks)
        
    text = str(raw_text).strip()
    
    # Sometimes the model might accidentally write "Richard Feynman: " at the start
    # due to the prompt. We should strip it if it happens.
    prefixes_to_strip = [
        "Richard Feynman: ",
        "Feynman: ",
        "Me: ",
        "I think: "
    ]
    
    for prefix in prefixes_to_strip:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
            
    # Stylize implicit citations (e.g., "[Source 1]") to look like Wikipedia-style superscripts
    # Note: Streamlit handles standard markdown natively, but we can standardize the look.
    text = re.sub(r'\[Source (\d+)\]', r'<sup>[\1]</sup>', text, flags=re.IGNORECASE)
    
    return text


def get_feynman_greeting() -> str:
    """Return a random, in-character greeting for the start of a chat session."""
    import random
    
    greetings = [
        "Hello there! What kind of physics problem are we looking at today?",
        "Hi! You know, I was just thinking about how strange nature is. What's on your mind?",
        "Greetings! Do you have a question? I love questions.",
        "Well, hello! Let's figure something out together. What are we curious about today?"
    ]
    return random.choice(greetings)
