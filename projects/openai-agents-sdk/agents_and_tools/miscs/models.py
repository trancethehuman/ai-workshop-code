from pydantic import BaseModel
from typing import List, Optional


# Document models moved from retrieve_founder_articles.py
class BaseDocument(BaseModel):
    """Base document properties without score"""

    text: str
    id: Optional[str] = None


class Document(BaseDocument):
    """Document with optional score"""

    score: Optional[float] = None


class RetrievalResponse(BaseModel):
    """Response from the retrieval API"""

    documents: List[Document]
    average_relevancy: float
    ndcg: float
    question: str
