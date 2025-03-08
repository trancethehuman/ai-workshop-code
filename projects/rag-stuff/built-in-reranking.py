from dotenv import load_dotenv
from typing import List, Dict

# Import needed functions from modules
from retrieval import retrieve_documents
from llm import llm_query, build_prompt
from eval import print_evaluation_results
from models import MODELS, QuestionContext, QuestionResult

load_dotenv()


def process_question_with_vectorize_rerank(question: str) -> QuestionContext:
    """Process a single question through the RAG pipeline using Vectorize's reranking"""
    print(f"\nProcessing question: {question}")

    # Step 1: Retrieve and rerank documents in a single call to Vectorize
    rag_retrieval = retrieve_documents(
        question=question,
        num_results=10,
        rerank=True,  # Use Vectorize's built-in reranking
    )
    print(f"Retrieved and reranked {len(rag_retrieval.documents)} documents")

    # Step 2: Create context from the documents
    document_texts = [doc.text for doc in rag_retrieval.documents]
    context = "\n\n".join(document_texts)

    # Step 3: Build prompt with context and question
    prompt = build_prompt(question, context)

    # Return the prepared data
    return QuestionContext(
        question=question,
        documents=rag_retrieval.documents,
        context=context,
        prompt=prompt,
        raw_documents=document_texts,
    )


# Main execution
if __name__ == "__main__":
    # Example questions
    user_queries = [
        "what is Jeff Bezos's leadership philosophy?",
        "how did Jeff Bezos approach risk and failure?",
    ]

    # Process each question and query model
    results: List[QuestionResult] = []

    for query in user_queries:
        # Process the question with Vectorize reranking
        context = process_question_with_vectorize_rerank(query)

        # Store model responses for this question
        model_responses: Dict[str, str] = {}

        # Query the model(s)
        for model in MODELS:
            print(f"\nQuerying {model} with the context...")
            model_output = llm_query(context.prompt, model)
            model_responses[model] = model_output

        # Create the result structure
        result = QuestionResult(
            question=query,
            documents=context.documents,
            model_responses=model_responses,
        )

        results.append(result)

    # Print results
    print_evaluation_results(results)
