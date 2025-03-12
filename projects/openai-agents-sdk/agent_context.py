from dataclasses import dataclass
from typing import List, Optional

from models import Document


# Define our context class to track state between interactions
@dataclass
class AgentContext:
    """Context for storing information between agent interactions"""

    recent_searches: List[str] = None
    recent_documents: List[Document] = None
    last_tool_used: Optional[str] = None  # Track the last tool used

    def __post_init__(self):
        if self.recent_searches is None:
            self.recent_searches = []
        if self.recent_documents is None:
            self.recent_documents = []

    def add_search(self, query: str):
        """Track searches to avoid repetition"""
        self.recent_searches.append(query)

    def add_documents(self, docs: List[Document]):
        """Store retrieved documents"""
        if self.recent_documents is None:
            self.recent_documents = []
        self.recent_documents.extend(docs)

    def set_last_tool(self, tool_name: str):
        """Track the last tool used"""
        self.last_tool_used = tool_name
