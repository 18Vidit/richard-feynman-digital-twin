"""
Short-Term Memory Buffer — Manages the current conversation context.
Maintains a sliding window of recent conversation history to allow
Feynman to answer follow-up questions effectively without exceeding
the LLM context limits or forgetting what was just discussed.
"""

from typing import List, Tuple


class ShortTermMemory:
    """A simple sliding window conversation buffer."""
    
    def __init__(self, max_exchanges: int = 5):
        """
        Initialize the memory buffer.
        
        Args:
            max_exchanges: The maximum number of Question/Answer pairs to keep in history.
                           (e.g., 5 exchanges = 10 messages total)
        """
        self.max_exchanges = max_exchanges
        self.history: List[Tuple[str, str]] = []
        
    def add_exchange(self, human_message: str, ai_message: str):
        """Add a new conversation exchange to the buffer."""
        self.history.append((human_message, ai_message))
        
        # Prune if we exceed the max window size
        if len(self.history) > self.max_exchanges:
            # Remove the oldest exchange
            self.history.pop(0)
            
    def get_formatted_history(self) -> List[tuple[str, str]]:
        """
        Get the history formatted for LangChain ChatPromptTemplate.
        Returns a list of tuples: [("human", msg1), ("ai", resp1), ...]
        """
        formatted = []
        for human_msg, ai_msg in self.history:
            formatted.append(("human", human_msg))
            formatted.append(("ai", ai_msg))
        return formatted
    
    def get_raw_history(self) -> List[Tuple[str, str]]:
        """Get the raw list of (human, ai) tuples."""
        return self.history
    
    def clear(self):
        """Clear the current session memory."""
        self.history = []
