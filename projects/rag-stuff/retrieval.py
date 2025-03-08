import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from models import Document

load_dotenv()


class RetrievalResponse(BaseModel):
    """Response from the retrieval API"""

    documents: List[Document]
    average_relevancy: float
    ndcg: float
    question: str


retrieval_endpoint = os.getenv("VECTORIZE_ENDPOINT")
if retrieval_endpoint is None:
    raise ValueError("VECTORIZE_ENDPOINT environment variable is not set")

headers = {
    "Content-Type": "application/json",
    "Authorization": os.getenv("VECTORIZE_TOKEN"),
}


# Function to retrieve documents from the vector store
def retrieve_documents(
    question: str, num_results: int = 10, rerank: bool = False
) -> RetrievalResponse:
    """
    Retrieve documents from Vectorize

    Args:
        question: The search query
        num_results: Number of results to return (default: 10)
        rerank: Whether to use Vectorize's built-in reranking (default: False)

    Returns:
        Retrieval response with documents
    """
    print(f"Searching for documents related to: {question}")

    # Prepare data payload
    retrieval_data = {
        "question": question,
        "numResults": num_results,
        "rerank": rerank,
    }

    # Ensure endpoint is not None
    if retrieval_endpoint is None:
        raise ValueError("Retrieval endpoint cannot be None")

    # Make the API request
    response = requests.post(retrieval_endpoint, headers=headers, json=retrieval_data)
    response.raise_for_status()
    result_json = response.json()

    # Parse the response with our Pydantic model
    return RetrievalResponse(**result_json)
