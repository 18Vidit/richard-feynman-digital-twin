"""
Document Loader — Reads .txt files with YAML frontmatter metadata.
Each Feynman document has a YAML frontmatter block (between --- delimiters)
containing metadata like title, author, year, source_type, topic, and source_url.

This module:
1. Discovers all .txt files under data/richard-feynman/
2. Parses YAML frontmatter into structured metadata
3. Returns LangChain Document objects ready for chunking
"""

import re
from pathlib import Path
from typing import Optional
import yaml
from langchain_core.documents import Document
from config import DATA_DIR, DATA_SUBDIRS, CATEGORY_MAP


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """
    Extract YAML frontmatter and body from a text file.
    Args:
        text: Raw file content with optional YAML frontmatter.
        
    Returns:
        Tuple of (metadata_dict, body_text).
        If no frontmatter found, returns ({}, full_text).
    """
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, text, re.DOTALL)
    
    if match:
        try:
            metadata = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            metadata = {}
        body = match.group(2).strip()
        return metadata, body
    
    return {}, text.strip()


def infer_category(filepath: Path) -> str:
    """
    Infer the document category from its directory path.
    E.g., data/richard-feynman/technical/simulating_physics.txt → 'technical'
    """
    for category, dir_path in DATA_SUBDIRS.items():
        try:
            filepath.relative_to(dir_path)
            return category
        except ValueError:
            continue
    return "unknown"


def load_single_document(filepath: Path) -> Optional[Document]:
    """
    Load a single .txt file into a LangChain Document with rich metadata.
    Metadata includes:
    - source: file path
    - title: from YAML or filename
    - author: always 'Richard P. Feynman'
    - year: from YAML (int or str)
    - source_type: paper/lecture/interview/etc.
    - topic: from YAML or title
    - category: inferred from directory
    - source_url: if available
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"Could not read {filepath.name}: {e}")
        return None
    
    frontmatter, body = parse_frontmatter(text)
    
    if not body or len(body.strip()) < 50:
        print(f"Skipping {filepath.name}: too short ({len(body)} chars)")
        return None
    
    category = infer_category(filepath)
    
    # Build metadata:refer YAML values, fall back to inferred
    metadata = {
        "source": str(filepath),
        "filename": filepath.name,
        "title": frontmatter.get("title", filepath.stem.replace("_", " ").title()),
        "author": frontmatter.get("author", "Richard P. Feynman"),
        "year": str(frontmatter.get("year", "unknown")),
        "source_type": frontmatter.get("source_type", CATEGORY_MAP.get(category, "unknown")),
        "topic": frontmatter.get("topic", frontmatter.get("title", filepath.stem.replace("_", " "))),
        "category": category,
        "source_url": frontmatter.get("source_url", ""),
    }
    
    return Document(page_content=body, metadata=metadata)


def load_all_documents(data_dir: Optional[Path] = None) -> list[Document]:
    """
    Load all .txt documents from the Feynman data directory.
    Returns:
        List of LangChain Document objects with metadata.
    """
    data_dir = data_dir or DATA_DIR
    
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    txt_files = sorted(data_dir.rglob("*.txt"))
    
    if not txt_files:
        raise FileNotFoundError(f"No .txt files found in {data_dir}")
    
    print(f"Found {len(txt_files)} documents in {data_dir}")
    
    documents = []
    for filepath in txt_files:
        doc = load_single_document(filepath)
        if doc:
            documents.append(doc)
            print(f"Loaded: {filepath.name} "
                  f"({len(doc.page_content):,} chars, "
                  f"year={doc.metadata['year']}, "
                  f"type={doc.metadata['source_type']})")
    
    print(f"\nSuccessfully loaded {len(documents)}/{len(txt_files)} documents")
    return documents


if __name__ == "__main__":
    # Quick test: load all documents and show summary
    docs = load_all_documents()
    
    print("\n" + "=" * 60)
    print("DOCUMENT SUMMARY")
    print("=" * 60)
    
    total_chars = sum(len(d.page_content) for d in docs)
    
    # Count by category
    from collections import Counter
    cats = Counter(d.metadata["category"] for d in docs)
    
    print(f"Total documents: {len(docs)}")
    print(f"Total characters: {total_chars:,}")
    print(f"\nBy category:")
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")
