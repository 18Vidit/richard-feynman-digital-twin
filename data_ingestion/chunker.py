"""
Smart Text Chunker — Splits documents into semantically coherent chunks.
Uses LangChain's RecursiveCharacterTextSplitter with a split hierarchy:
  1. Double newlines (paragraph boundaries)
  2. Single newlines (line breaks)
  3. Sentences (period + space)
  4. Words (spaces)
  5. Characters (last resort)

Each chunk inherits the parent document's metadata, plus:
  - chunk_index: position within the document
  - total_chunks: how many chunks the document was split into
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_SIZE, CHUNK_OVERLAP, SEPARATORS


def create_chunker(
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    separators: list[str] | None = None,
) -> RecursiveCharacterTextSplitter:
    """
    Create a text splitter configured for Feynman's writing style.
    
    His documents tend to have:
    - Long, flowing paragraphs (physics explanations)
    - Section headers (numbered sections like "1. INTRODUCTION")
    - Mathematical notation inline
    
    We use relatively large chunks (1000 chars ≈ 500 tokens) to preserve
    context for complex physics explanations, with 200-char overlap.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators or SEPARATORS,
        length_function=len,
        is_separator_regex=False,
    )


def chunk_documents(
    documents: list[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """
    Split a list of documents into smaller chunks, preserving metadata.
    
    Each chunk gets additional metadata:
    - chunk_index: 0-based position within its parent document
    - total_chunks: total number of chunks from the parent document
    
    Args:
        documents: List of LangChain Documents to chunk.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Character overlap between adjacent chunks.
        
    Returns:
        List of chunked Document objects with enriched metadata.
    """
    splitter = create_chunker(chunk_size, chunk_overlap)
    
    all_chunks = []
    
    for doc in documents:
        # Split this document into chunks
        chunks = splitter.split_documents([doc])
        
        # Enrich each chunk with positional metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = len(chunks)
        
        all_chunks.extend(chunks)
    
    print(f"Chunked {len(documents)} documents → {len(all_chunks)} chunks")
    print(f"Average chunk size: {sum(len(c.page_content) for c in all_chunks) // max(len(all_chunks), 1)} chars")
    
    return all_chunks


if __name__ == "__main__":
    # quick test: load and chunk docs
    from data_ingestion.loader import load_all_documents
    
    docs = load_all_documents()
    chunks = chunk_documents(docs)
    
    # show a sample chunk
    if chunks:
        sample = chunks[0]
        print(f"\n{'='*60}")
        print(f"SAMPLE CHUNK (from {sample.metadata['title']})")
        print(f"{'='*60}")
        print(f"Metadata: { {k: v for k, v in sample.metadata.items() if k != 'source'} }")
        print(f"Content ({len(sample.page_content)} chars):")
        print(sample.page_content[:500])
        print("...")
