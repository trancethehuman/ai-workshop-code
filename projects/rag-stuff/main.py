import requests
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from litellm import completion
from quotientai import QuotientAI
from typing import List, Dict, Any

load_dotenv()

quotient = QuotientAI(api_key=os.getenv("QUOTIENT_API_KEY"))

quotient_logger = quotient.logger.init(
    # Required
    app_name="founder-tribune",
    environment="dev",
    # optional: dynamic labels for slicing/dicing analytics e.g. by customer, feature, etc
    tags={"model": "gpt-4o-mini", "feature": "customer-support"},
    hallucination_detection=True,
    # set the sampling rate to 1.0 to run detection on 100% of logs
    hallucination_detection_sample_rate=1.0,
)


class Document(BaseModel):
    chunk_id: str
    id: str
    index: str
    org_id: str
    origin: str
    origin_id: str
    pipeline_id: str
    similarity: float
    source: str
    source_display_name: str
    text: str
    total_chunks: str
    unique_source: str
    relevancy: float


class RetrievalResponse(BaseModel):
    documents: list[Document]
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

# Default data for retrieval
retrieval_data = {
    "question": "",
    "numResults": 10,
    "rerank": False,
}

# List of models to query
MODELS = [
    "groq/gemma2-9b-it",
    "groq/llama-3.2-1b-preview",
    "groq/llama3-8b-8192",
    "together_ai/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
]


# Function to query an LLM model with a specific model
def llm_query(user_query: str, model: str) -> str:
    try:
        # Call the LLM through LiteLLM with the specified model
        response = completion(
            model=model,
            messages=[{"role": "user", "content": user_query}],
        )

        # Return the response content
        return response.choices[0].message.content
    except Exception as e:
        error_message = f"Error querying {model}: {e}"
        print(error_message)
        return error_message


# Function to retrieve documents from the vector store
def retrieve_documents(question: str) -> RetrievalResponse:
    print(f"Searching for documents related to: {question}")
    retrieval_data["question"] = question
    response = requests.post(retrieval_endpoint, headers=headers, json=retrieval_data)
    response.raise_for_status()
    result_json = response.json()

    # Parse the response with our Pydantic model
    return RetrievalResponse(**result_json)


# The RAG pipeline combining vector search and LLM
def run_rag_pipeline(
    questions: List[str] = ["what were some lessons from Jeff Bezos?"],
) -> List[Dict[str, Any]]:
    results = []

    for question in questions:
        # Step 1: Get relevant documents from the vector store (once per question)
        rag_retrieval = retrieve_documents(question)

        # Step 2: Extract relevant content from retrieved documents
        documents = []
        for doc in rag_retrieval.documents:
            documents.append(doc.text)

        context = "\n\n".join(documents)

        # Step 3: Format prompt for the LLM with the retrieved context
        prompt = f"""Based on the following information about Jeff Bezos, summarize 3-5 key business lessons from Jeff Bezos:
            {context}
            Please provide a concise summary of the most important business lessons from Bezos mentioned in these documents.
            """

        question_results = {
            "question": question,
            "documents": rag_retrieval.documents,
            "model_responses": {},
        }

        # Step 4: Query each LLM model with the prompt
        for model in MODELS:
            print(f"\nQuerying {model} with the retrieved context...")
            rag_generation = llm_query(prompt, model)

            # Step 5: Check for hallucination
            response = quotient_logger.log(
                user_query=question,
                model_output=rag_generation,
                # list of strings of retrieved documents from your application
                documents=documents,
            )

            # Store the model's response
            question_results["model_responses"][model] = rag_generation

        results.append(question_results)

    return results


# Main execution
if __name__ == "__main__":
    # List of user queries to process
    user_queries = [
        "what were some lessons from Jeff Bezos?",
        "how did Jeff Bezos approach risk and failure?",
        "what is Jeff Bezos's leadership philosophy?",
    ]

    # Run the RAG pipeline with multiple queries
    results = run_rag_pipeline(user_queries)

    # Print the results
    for result in results:
        print("\n" + "=" * 80)
        print(f"QUESTION: {result['question']}")
        print("=" * 80)

        for model, answer in result["model_responses"].items():
            print(f"\nMODEL: {model}")
            print("-" * 50)
            print("ANSWER:")
            print(answer)
            print("-" * 50)
