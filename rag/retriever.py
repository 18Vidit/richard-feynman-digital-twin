"""
Retriever — Queries ChromaDB for the most relevant Feynman content.
Given a user query, this module:
1. Embeds the query using the same embedding model
2. Performs similarity search in ChromaDB
3. Returns the top-k most relevant chunks with metadata

Supports optional metadata filtering (e.g., only lectures, only pre-1965).
"""

from pathlib import Path
import chromadb
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings  # pyrefly: ignore [missing-import]

from config import (
    EMBEDDING_MODEL,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
    RETRIEVAL_TOP_K,
)


def get_retriever_components(
    persist_dir: Path | None = None,
    collection_name: str = CHROMA_COLLECTION_NAME,
) -> tuple[chromadb.Collection, HuggingFaceEmbeddings]:
    """Get ChromaDB collection and embedding model for retrieval."""
    persist_dir = persist_dir or CHROMA_PERSIST_DIR
    
    client = chromadb.PersistentClient(path=str(persist_dir))
    collection = client.get_collection(name=collection_name)
    
    embed_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
    )
    
    return collection, embed_model


def retrieve(
    query: str,
    top_k: int = RETRIEVAL_TOP_K,
    where_filter: dict | None = None,
    persist_dir: Path | None = None,
    collection_name: str = CHROMA_COLLECTION_NAME,
) -> list[Document]:
    """
    Retrieve the most relevant chunks for a given query.
    Args:
        query: User's question or search query.
        top_k: Number of chunks to retrieve.
        where_filter: Optional ChromaDB metadata filter.
            Example: {"category": "lectures"} to search only lectures.
            Example: {"source_type": {"$in": ["paper", "lecture"]}}
        persist_dir: ChromaDB persistence directory.
        collection_name: ChromaDB collection name.
    Returns:
        List of LangChain Document objects, sorted by relevance (best first).
    """
    collection, embed_model = get_retriever_components(persist_dir, collection_name)

    # Embed the query
    query_embedding = embed_model.embed_query(query)

    # Build query kwargs
    query_kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }
    
    if where_filter:
        query_kwargs["where"] = where_filter
    
    # Search ChromaDB
    results = collection.query(**query_kwargs)
    
    # Convert to LangChain Documents
    documents = []
    
    if results and results["documents"]:
        for doc_text, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            # Add similarity score to metadata (convert distance to similarity)(COSINE)
            metadata["relevance_score"] = round(1 - distance, 4)
            
            documents.append(Document(
                page_content=doc_text,
                metadata=metadata,
            ))
    
    return documents


def retrieve_with_sources(
    query: str,
    top_k: int = RETRIEVAL_TOP_K,
    **kwargs,
) -> tuple[list[Document], list[dict]]:
    """
    Retrieve chunks and return them along with structured source info.
    Returns:
        Tuple of (documents, sources) where sources is a list of dicts
        with title, year, category, relevance_score for the citation overlay.
    """
    docs = retrieve(query, top_k, **kwargs)
    
    sources = []
    for doc in docs:
        sources.append({
            "title": doc.metadata.get("title", "Unknown"),
            "year": doc.metadata.get("year", "Unknown"),
            "category": doc.metadata.get("category", "Unknown"),
            "source_type": doc.metadata.get("source_type", "Unknown"),
            "relevance_score": doc.metadata.get("relevance_score", 0),
            "chunk_index": doc.metadata.get("chunk_index", 0),
            "filename": doc.metadata.get("filename", "Unknown"),
        })
    
    return docs, sources


if __name__ == "__main__":
    # Ensure we can import from root when running directly as a script
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Test retrieval with sample queries
    test_queries = [
        "What is quantum electrodynamics?",
        "Tell me about the Challenger disaster",
        "How does Feynman explain atoms?",
        "What is the principle of least action?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print(f"{'='*60}")
        docs, sources = retrieve_with_sources(query, top_k=3)
        for i, (doc, src) in enumerate(zip(docs, sources)):
            print(f"\nResult {i+1} (score: {src['relevance_score']:.3f}):")
            print(f"Source: {src['title']} ({src['year']}) [{src['category']}]")
            print(f"Preview: {doc.page_content[:200]}...")
