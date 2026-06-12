"""
Embedder — Embeds chunked documents and stores them in ChromaDB.
Uses HuggingFace local embeddings (all-MiniLM-L6-v2) to create dense
vector representations, then persists them in a local ChromaDB instance.
This prevents hitting API rate limits during massive document ingestion.

The ChromaDB collection stores:
  - Document text (the chunk content)
  - Embedding vector (384-dimensional)
  - Metadata (title, year, category, source_type, etc.)
  - A unique ID per chunk
"""

import hashlib
import time
from pathlib import Path

import chromadb
from langchain_core.documents import Document
# pyrefly: ignore [missing-import]
from langchain_huggingface import HuggingFaceEmbeddings

from config import (
    EMBEDDING_MODEL,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
)


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Create the HuggingFace local embedding model instance."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
    )


def get_chroma_client(persist_dir: Path | None = None) -> chromadb.ClientAPI:
    """Create a persistent ChromaDB client."""
    persist_dir = persist_dir or CHROMA_PERSIST_DIR
    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_dir))


def generate_chunk_id(chunk: Document, index: int) -> str:
    """
    Generate a deterministic, unique ID for a chunk.
    """
    source = chunk.metadata.get("source", "unknown")
    chunk_idx = chunk.metadata.get("chunk_index", index)
    raw = f"{source}::chunk_{chunk_idx}"
    return hashlib.md5(raw.encode()).hexdigest()


def embed_and_store(
    chunks: list[Document],
    persist_dir: Path | None = None,
    collection_name: str = CHROMA_COLLECTION_NAME,
    batch_size: int = 500,  # Larger batches are safe for local models
) -> int:
    """
    Embed all chunks locally and store them in ChromaDB.
    """
    if not chunks:
        print("Warning: No chunks to embed!")
        return 0
    
    print(f"Embedding {len(chunks)} chunks locally with {EMBEDDING_MODEL}...")
    
    # Initialize clients
    embed_model = get_embedding_model()
    chroma_client = get_chroma_client(persist_dir)
    
    # Get or create the collection
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    
    existing_count = collection.count()
    if existing_count > 0:
        print(f"Found {existing_count} existing vectors (will upsert)")
    
    total_stored = 0
    start_time = time.time()
    total_batches = (len(chunks) + batch_size - 1) // batch_size
    
    for batch_start in range(0, len(chunks), batch_size):
        batch_end = min(batch_start + batch_size, len(chunks))
        batch = chunks[batch_start:batch_end]
        batch_num = batch_start // batch_size + 1
        
        print(f"  [{batch_num}/{total_batches}] "
              f"chunks {batch_start+1}-{batch_end}...", end=" ", flush=True)
        
        # Prepare batch data
        texts = [chunk.page_content for chunk in batch]
        ids = [generate_chunk_id(chunk, batch_start + i) for i, chunk in enumerate(batch)]
        
        # Sanitize metadata
        metadatas = []
        for chunk in batch:
            meta = {}
            for k, v in chunk.metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    meta[k] = v
                else:
                    meta[k] = str(v)
            metadatas.append(meta)
        
        # Embed using HuggingFace locally (fast, no rate limits)
        embeddings = embed_model.embed_documents(texts)
        
        # Upsert into ChromaDB
        collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        
        total_stored += len(batch)
        print(f"OK ({total_stored}/{len(chunks)})")
    
    elapsed = time.time() - start_time
    print(f"\nDone! Stored {total_stored} chunks in ChromaDB ({collection_name})")
    print(f"Persisted to: {persist_dir or CHROMA_PERSIST_DIR}")
    print(f"Collection size: {collection.count()} total vectors")
    print(f"Total time: {elapsed / 60:.1f} min")
    
    return total_stored


def get_collection_stats(
    persist_dir: Path | None = None,
    collection_name: str = CHROMA_COLLECTION_NAME,
) -> dict:
    """Get stats about the current ChromaDB collection."""
    client = get_chroma_client(persist_dir)
    
    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        sample = collection.peek(limit=5)
        
        return {
            "collection_name": collection_name,
            "total_vectors": count,
            "sample_ids": sample.get("ids", []),
            "sample_metadata": sample.get("metadatas", []),
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    from data_ingestion.loader import load_all_documents
    from data_ingestion.chunker import chunk_documents
    
    docs = load_all_documents()
    chunks = chunk_documents(docs)
    stored = embed_and_store(chunks)
    print("\n" + "=" * 60)
    print(f"Collection stats: {get_collection_stats()}")
