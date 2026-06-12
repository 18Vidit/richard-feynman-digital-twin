"""
Long-Term Memory Store — SQLite persistence for user facts.
Stores facts, interests, and preferences learned about the user
across sessions. This allows Feynman to remember who he's talking
to ("Oh, you're the engineering student who likes the double slit!").
"""

import sqlite3
import datetime
from pathlib import Path
from typing import List, Dict, Any


class LongTermMemoryStore:
    """SQLite-backed storage for persistent user memories."""
    
    def __init__(self, db_path: str | Path = "data/memory.db"):
        """Initialize the database connection and schema."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        
    def _init_db(self):
        """Create the schema if it doesn't exist."""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                importance_score INTEGER DEFAULT 1
            )
        ''')
        self.conn.commit()
        
    def add_memory(self, session_id: str, memory_type: str, content: str, importance: int = 1):
        """Add a new memory to the persistent store."""
        cursor = self.conn.cursor()
        timestamp = datetime.datetime.now(datetime.UTC).isoformat()
        
        cursor.execute(
            '''INSERT INTO memories (session_id, timestamp, memory_type, content, importance_score)
               VALUES (?, ?, ?, ?, ?)''',
            (session_id, timestamp, memory_type, content, importance)
        )
        self.conn.commit()
        
    def get_memories(self, session_id: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve long term memories. 
        If session_id is provided, can filter by it, but for a Digital Twin,
        we usually want ALL memories to pass as persistent context.
        """
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM memories"
        params = []
        
        if session_id:
            query += " WHERE session_id = ?"
            params.append(session_id)
            
        query += " ORDER BY importance_score DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
        
    def format_memories_for_prompt(self, limit: int = 10) -> str:
        """Format the top memories into a string block for the LLM prompt."""
        memories = self.get_memories(limit=limit)
        if not memories:
            return "No prior knowledge about the user."
            
        lines = []
        for mem in memories:
            lines.append(f"- [{mem['memory_type'].upper()}] {mem['content']}")
            
        return "\n".join(lines)
        
    def close(self):
        """Close the database connection."""
        self.conn.close()
