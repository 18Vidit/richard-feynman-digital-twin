"""
Digital Twin of Richard Feynman — Centralized Configuration
All paths, model settings, chunking parameters, and prompts in one place.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables 
load_dotenv()

# Paths 
PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_DIR = PROJECT_ROOT / "data" / "richard-feynman"
CHROMA_PERSIST_DIR = PROJECT_ROOT / "chroma_db"
MEMORY_DB_PATH = PROJECT_ROOT / "memory.db"

# Data subdirectories 
DATA_SUBDIRS = {
    "technical": DATA_DIR / "technical",
    "lectures": DATA_DIR / "lectures",
    "persona": DATA_DIR / "persona",
    "interviews": DATA_DIR / "interviews",
    "speeches": DATA_DIR / "speeches",
    "books": DATA_DIR / "books",
    "letters": DATA_DIR / "letters",
    "testimony": DATA_DIR / "testimony",
}

# Gemini Model Settings 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_TEMPERATURE = 0.7      # Slightly creative for Feynman's personality
LLM_MAX_OUTPUT_TOKENS = 2048

# Chunking Parameters 
CHUNK_SIZE = 1000           # ~500 tokens ≈ 1000 characters
CHUNK_OVERLAP = 200         # Overlap to preserve context across boundaries
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]  # Split hierarchy

# Retrieval Parameters 
RETRIEVAL_TOP_K = 5         # Number of chunks to retrieve per query
CHROMA_COLLECTION_NAME = "feynman_knowledge"

# Memory Parameters 
STM_WINDOW_SIZE = 15        # Keep last N exchanges in short-term memory
LTM_IMPORTANCE_THRESHOLD = 0.6  # Minimum score to persist to long-term memory

# Category → source_type mapping (for metadata enrichment) 
CATEGORY_MAP = {
    "technical": "paper",
    "lectures": "lecture",
    "persona": "persona",
    "interviews": "interview",
    "speeches": "speech",
    "books": "book",
    "letters": "letter",
    "testimony": "testimony",
}

# Feynman's death year (for timeline awareness) 
FEYNMAN_DEATH_YEAR = 1988
