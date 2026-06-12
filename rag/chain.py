"""
RAG Chain  Retrieval Augmented Generation with Gemini (Persona Engine).
Combines retrieved Feynman content with the user's query and sends it
to Gemini 2.5 Flash, structured by the Feynman Persona System Prompt.
"""

from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI

from config import (
    GOOGLE_API_KEY,
    LLM_TEMPERATURE,
    LLM_MAX_OUTPUT_TOKENS,
    RETRIEVAL_TOP_K,
)
import config
from rag.retriever import retrieve_with_sources
from persona.prompts import get_feynman_prompt


def get_llm() -> ChatGoogleGenerativeAI:  #get_llm is from Langchain library, it creates an instance of the LLM.
    """Create the Gemini LLM instance."""
    return ChatGoogleGenerativeAI( #instantiating the LLM with the given parameters
        model=config.LLM_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=LLM_TEMPERATURE,
        max_output_tokens=LLM_MAX_OUTPUT_TOKENS,
    )


def format_context(documents: list[Document]) -> str: #format_context is a function that formats the retrieved documents into a context string for the prompt.
    """Format retrieved documents into a context string for the prompt."""
    context_parts = []
    for i, doc in enumerate(documents, 1): #enumerate is used to get the index of the document and the document itself.
        title = doc.metadata.get("title", "Unknown") #get is used to get the value of the key from the metadata dictionary. if the key is not found, it returns the default value.
        year = doc.metadata.get("year", "Unknown")
        source_type = doc.metadata.get("source_type", "Unknown")
        
        context_parts.append( #appends the formatted context to the context_parts list.
            f"[Source {i}: {title} ({year}) — {source_type}]\n"
            f"{doc.page_content}\n"
        )
    
    return "\n---\n".join(context_parts)


def format_sources(sources: list[dict]) -> str: #format_sources is a function that formats the retrieved sources into a context string for the prompt.
    """Format source metadata for the prompt."""
    lines = []
    for i, src in enumerate(sources, 1): #enumerate is used to get the index of the document and the document itself.
        lines.append( #appends the formatted sources to the lines list.
            f"[{i}] \"{src['title']}\" ({src['year']}) "
            f"— Type: {src['source_type']}, "
            f"Relevance: {src['relevance_score']:.1%}"
        )
    return "\n".join(lines)


def rag_query( #rag_query is a function that runs a full RAG query: retrieve → format → generate.
    question: str, #the question asked by the user.
    top_k: int = RETRIEVAL_TOP_K, #the number of context chunks to retrieve.
    where_filter: dict | None = None, #optional metadata filter for retrieval.
    chat_history: list[tuple[str, str]] | None = None, #formatted history from ShortTermMemory buffer.
    user_memories: str = "No prior knowledge about the user.", #No prior knowledge about the user.
) -> dict: #Returns a dictionary with the answer, sources, and context documents.
    """
    Run a full RAG query: retrieve → format → generate.
    Args:
        question: The user's question.
        top_k: Number of context chunks to retrieve.
        where_filter: Optional metadata filter for retrieval.
        chat_history: Formatted history from ShortTermMemory buffer.
        
    Returns:
        Dict with keys:
        - answer: The generated response text
        - sources: List of source metadata dicts
        - context_docs: The raw retrieved documents
    """
    # Initialize empty history if none provided
    chat_history = chat_history or [] #if no chat history is provided, it initializes an empty list.
    
    # Step 1: Retrieve relevant chunks
    docs, sources = retrieve_with_sources(question, top_k=top_k, where_filter=where_filter) #retrieve_with_sources is a function that retrieves relevant chunks from the knowledge base.
    
    if not docs: #if no documents are retrieved, it returns an empty dictionary.
        return {
            "answer": "I don't know anything about that! I couldn't find it in my notes or lectures.",
            "sources": [],
            "context_docs": [],
        }
    
    # Step 2: Format context and sources
    context = format_context(docs)
    sources_text = format_sources(sources)
    
    # Step 3: Build prompt and generate
    prompt = get_feynman_prompt() #get_feynman_prompt is a function that returns the Feynman persona prompt.
    llm = get_llm() #get_llm is a function that returns the Gemini LLM instance.
    
    chain = prompt | llm #chain is a Langchain object that combines the prompt and the LLM.
    
    response = chain.invoke({ #invoke is a function that runs the RAG query.
        "context": context,
        "sources": sources_text,
        "question": question,
        "chat_history": chat_history,
        "user_memories": user_memories,
    })
    
    return {
        "answer": response.content,
        "sources": sources,
        "context_docs": docs,
    }


if __name__ == "__main__":
    # Interactive test
    print("=" * 60)
    print("RAG Chain Test — Ask Feynman's writings anything!")
    print("=" * 60)
    
    test_questions = [
        "What did Feynman think about quantum computers?",
        "How does Feynman explain what atoms are?",
        "What happened with the Challenger O-ring?",
    ]
    
    for q in test_questions: #iterates through the test questions.
        print(f"\n{'─'*60}")
        print(f"Question: {q}")
        print(f"{'─'*60}")
        
        result = rag_query(q)
        
        print(f"\nAnswer:\n{result['answer']}")
        
        if result["sources"]:
            print(f"\nSources used:")
            for src in result["sources"]:
                print(f"   • {src['title']} ({src['year']}) "
                      f"[{src['category']}] — {src['relevance_score']:.1%}")
