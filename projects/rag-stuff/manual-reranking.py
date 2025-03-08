from dotenv import load_dotenv
from typing import List, Dict

# Import needed functions from modules
from retrieval import retrieve_documents
from llm import query_model, build_prompt
from eval import print_evaluation_results
from rerank_wrapper import CohereReranker
from models import MODELS, QuestionContext, QuestionResult

load_dotenv()

# Initialize the reranker
reranker = CohereReranker()


def process_question(question: str) -> QuestionContext:
    """Process a single question through the RAG pipeline and return context"""
    print(f"\nProcessing question: {question}")

    # Step 1: Retrieve relevant documents
    rag_retrieval = retrieve_documents(question)
    print(f"Retrieved {len(rag_retrieval.documents)} documents")

    # Step 2: Extract content from documents for reranking
    document_texts = [doc.text for doc in rag_retrieval.documents]
    document_ids = [doc.id for doc in rag_retrieval.documents]

    # Filter out None values from document_ids
    document_ids = [doc_id for doc_id in document_ids if doc_id is not None]

    # Step 3: Rerank the documents
    print("Reranking documents...")
    reranked_docs = reranker.rerank(
        query=question,
        documents=document_texts,
        document_ids=document_ids,
        top_n=5,  # Get top 5 most relevant documents
    )
    print(f"Reranking complete - selected top {len(reranked_docs)} documents")

    # Step 4: Create context from reranked documents
    reranked_texts = [doc.text for doc in reranked_docs]
    context = "\n\n".join(reranked_texts)

    # Step 5: Build prompt with context and question using the function from llm.py
    prompt = build_prompt(question, context)

    # Return the prepared data as a QuestionContext object
    return QuestionContext(
        question=question,
        documents=reranked_docs,
        context=context,
        prompt=prompt,
        raw_documents=reranked_texts,
    )


# Main execution
if __name__ == "__main__":
    # List of user queries to process
    user_queries = [
        "what is Jeff Bezos's leadership philosophy?",
    ]

    # Process each question and then query each model
    results: List[QuestionResult] = []

    for query in user_queries:
        # Process the question to prepare context
        context = process_question(query)

        # Store model responses for this question
        model_responses: Dict[str, str] = {}

        # Query each model separately
        for model in MODELS:
            model_response = query_model(context, model)
            model_responses[model] = model_response

        # Create the final result structure
        result = QuestionResult(
            question=query,
            documents=context.documents,
            model_responses=model_responses,
        )

        results.append(result)

    # Print the evaluation results
    print_evaluation_results(results)
