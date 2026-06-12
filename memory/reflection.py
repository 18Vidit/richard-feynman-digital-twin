"""
Reflection Chain — Extracts facts from conversation history.
Uses Gemini to analyze the recent conversation history and extract
any persistent facts about the user (e.g., occupation, interests, goals).
These facts are then saved to the SQLite Long-Term Memory.
"""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from config import GOOGLE_API_KEY, LLM_MODEL
from langchain_google_genai import ChatGoogleGenerativeAI
from memory.sqlite_store import LongTermMemoryStore


class ExtractedFact(BaseModel):
    """A single fact extracted from the conversation."""
    memory_type: str = Field(description="Type of memory: 'fact', 'interest', or 'preference'")
    content: str = Field(description="The actual fact, e.g., 'The user is an engineering student.'")
    importance_score: int = Field(description="Score from 1 to 5 on how important this is to remember.")


class ReflectionOutput(BaseModel):
    """The structured output containing all extracted facts."""
    facts: list[ExtractedFact]


REFLECTION_PROMPT = """\
Analyze the following conversation between Richard Feynman (AI) and a User.
Extract any NEW, persistent facts about the user that would be useful for Feynman to remember in future conversations.

Types of facts to extract:
- Occupation, major, or background (e.g., "User is a physics student")
- Specific interests (e.g., "User is fascinated by quantum computing")
- Personal preferences or constraints (e.g., "User prefers simple explanations without math")

DO NOT extract facts about Feynman himself, or general facts about the world. ONLY extract facts about the USER.
If there are no new facts to extract, return an empty list.

CONVERSATION HISTORY:
{history}
"""


def extract_and_store_memories(
    history: list[tuple[str, str]],
    session_id: str,
    store: LongTermMemoryStore,
) -> int:
    """
    Run the reflection chain to extract memories and save them to the store.
    
    Returns:
        The number of new memories saved.
    """
    if not history:
        return 0
        
    # Format history into a readable string
    history_str = ""
    for human, ai in history:
        history_str += f"User: {human}\nFeynman: {ai}\n\n"
        
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.1,  # Keep it grounded
    )
    
    # We use LangChain's structured output parser to get JSON
    structured_llm = llm.with_structured_output(ReflectionOutput)
    prompt = ChatPromptTemplate.from_template(REFLECTION_PROMPT)
    chain = prompt | structured_llm
    
    try:
        result: ReflectionOutput = chain.invoke({"history": history_str})
        
        # Store extracted facts
        saved_count = 0
        for fact in result.facts:
            store.add_memory(
                session_id=session_id,
                memory_type=fact.memory_type,
                content=fact.content,
                importance=fact.importance_score
            )
            saved_count += 1
            
        return saved_count
        
    except Exception as e:
        print(f"Error during memory reflection: {e}")
        return 0
