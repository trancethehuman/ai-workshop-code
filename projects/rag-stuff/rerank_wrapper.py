import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from models import Document

load_dotenv()


class RerankResponse(BaseModel):
    """Response from the reranking API"""

    results: List[Dict[str, Any]]


class CohereReranker:
    """Wrapper for Cohere's Rerank API"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the reranker with an API key"""
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Cohere API key is required. Set COHERE_API_KEY environment variable or pass it explicitly."
            )

        self.base_url = "https://api.cohere.ai/v1/rerank"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def rerank(
        self,
        query: str,
        documents: List[str],
        document_ids: Optional[List[str]] = None,
        top_n: int = 10,
        model: str = "rerank-english-v2.0",
    ) -> List[Document]:
        """
        Rerank a list of documents based on their relevance to the query.
        """
        if document_ids and len(document_ids) != len(documents):
            raise ValueError(
                "If document_ids is provided, it must have the same length as documents"
            )

        # Maximum number of documents to rerank
        max_docs = min(top_n, len(documents))

        # Store original document texts for lookup
        original_docs = documents.copy()
        original_ids = (
            document_ids.copy()
            if document_ids
            else [str(i) for i in range(len(documents))]
        )

        # Prepare document entries for the API
        docs_for_api = []
        for i, doc in enumerate(documents[:max_docs]):
            doc_entry = {"text": doc}
            doc_entry["id"] = str(i)  # Use string index as ID
            docs_for_api.append(doc_entry)

        # Prepare the request payload
        data = {
            "query": query,
            "documents": docs_for_api,
            "top_n": max_docs,
            "model": model,
        }

        # Make the API request
        try:
            response = requests.post(self.base_url, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()

            # Get the results array
            results_array = result.get("results", [])

            # Parse and return the results
            reranked_docs = []

            for i, item in enumerate(results_array):
                # Get the relevance score
                score = item.get("relevance_score", 0.0)

                # Try to get document ID, fallback to index
                doc_index = i
                if (
                    "document" in item
                    and "id" in item["document"]
                    and item["document"]["id"]
                ):
                    # If there's a valid ID from API, try to parse it as an index
                    try:
                        doc_index = int(item["document"]["id"])
                    except (ValueError, TypeError):
                        # If ID isn't an integer index, keep using position index
                        pass

                # Make sure the index is valid
                if doc_index < 0 or doc_index >= len(original_docs):
                    doc_index = i

                # Use the document text from our original array
                if doc_index < len(original_docs):
                    doc_text = original_docs[doc_index]
                    doc_id = (
                        original_ids[doc_index]
                        if doc_index < len(original_ids)
                        else str(doc_index)
                    )
                else:
                    # Fallback to empty if somehow index is out of range
                    doc_text = ""
                    doc_id = ""

                # Create the document
                reranked_docs.append(
                    Document(
                        text=doc_text,
                        id=doc_id,
                        score=score,
                    )
                )

            return reranked_docs

        except requests.exceptions.RequestException as e:
            print(f"Error making request to Cohere Rerank API: {e}")
            raise

    def rerank_with_metadata(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        text_field: str = "text",
        id_field: str = "id",
        top_n: int = 10,
        model: str = "rerank-english-v2.0",
    ) -> List[Dict[str, Any]]:
        """
        Rerank a list of document dictionaries that include metadata.

        Args:
            query: The search query
            documents: List of document dictionaries with text and metadata
            text_field: The field name in each document that contains the text
            id_field: The field name for document ID
            top_n: Number of top results to return
            model: Reranking model to use

        Returns:
            List of original document dictionaries in reranked order with added relevance scores
        """
        # Extract document texts and IDs
        doc_texts = [doc.get(text_field, "") for doc in documents]
        doc_ids = [doc.get(id_field, str(i)) for i, doc in enumerate(documents)]

        # Get reranked results
        reranked_results = self.rerank(query, doc_texts, doc_ids, top_n, model)

        # Map results back to original documents with scores
        id_to_doc = {doc.get(id_field, str(i)): doc for i, doc in enumerate(documents)}
        result_docs = []

        for reranked_doc in reranked_results:
            if reranked_doc.id in id_to_doc:
                # Create a copy of the original document
                enriched_doc = dict(id_to_doc[reranked_doc.id])
                # Add the relevance score
                enriched_doc["relevance_score"] = reranked_doc.score
                result_docs.append(enriched_doc)

        return result_docs


# Example usage
if __name__ == "__main__":
    # Initialize the reranker
    reranker = CohereReranker()

    # Example documents
    documents = [
        "Jeff Bezos founded Amazon in 1994 as an online bookstore.",
        "Bezos often emphasizes the importance of customer obsession.",
        "One of Bezos's principles is to focus on long-term thinking over short-term gains.",
        "Bezos stepped down as CEO of Amazon in 2021.",
        "Under Bezos's leadership, Amazon expanded into cloud computing with AWS.",
        "Bezos believes in making high-quality decisions quickly with limited information.",
    ]

    # Example query
    query = "What are Jeff Bezos's business principles?"

    # Rerank the documents
    results = reranker.rerank(query, documents)

    # Print the results
    print(f"Query: {query}\n")
    for i, doc in enumerate(results):
        print(f"Rank {i + 1} (Score: {doc.score:.4f}): {doc.text}")
