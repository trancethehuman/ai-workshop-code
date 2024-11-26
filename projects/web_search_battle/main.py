from langsmith import Client
from reference import ground_truths
from tavily_search import get_response_tavily
from exa_search import get_response_exa
from gemini_search_grounding import get_response_google_grounding
from perplexity import get_response_perplexity
from dataset import create_evaluation_dataset
from evaluator import search_accuracy_evaluator
from langsmith.evaluation import evaluate

# Initialize client
langsmith_client = Client()

PROVIDERS = {
    "tavily": get_response_tavily,
    "exa": get_response_exa,
    "gemini": get_response_google_grounding,
    "perplexity": get_response_perplexity,
}


def generate_responses():
    """Generate responses from all providers for each ground truth query"""
    all_responses = []

    for truth in ground_truths:
        query = truth["input"]
        reference = truth["output"]
        print(f"\n--- Processing query: {query}")
        print(f"Reference answer: {reference}")

        for provider_name, provider_func in PROVIDERS.items():
            print(f"\nQuerying {provider_name}...")
            try:
                response = provider_func(query)
                print(f"{provider_name} response: {response['output']}")
                all_responses.append(
                    {
                        "query": query,
                        "reference": reference,
                        "provider": provider_name,
                        "output": response["output"],
                        "sources": response.get("sources", []),
                        "grounded": response.get("grounded", False),
                    }
                )
            except Exception as e:
                print(f"❌ Error with {provider_name} for query '{query}': {str(e)}")

    return all_responses


def run_evaluation():
    """Run the complete evaluation process"""
    print("Generating responses from all providers...")
    generate_responses()

    print("\nCreating evaluation dataset...")
    dataset = create_evaluation_dataset(PROVIDERS)

    print("\nRunning evaluations for each provider...")
    all_results = {}
    max_retries = 3

    # Run separate evaluation for each provider
    for provider in PROVIDERS.keys():
        print(f"\nEvaluating {provider}...")

        for attempt in range(max_retries):
            try:
                # Get examples for this provider's split
                provider_examples = list(
                    langsmith_client.list_examples(
                        dataset_name=dataset.name, splits=[provider]
                    )
                )

                if not provider_examples:
                    print(f"No examples found for provider {provider}")
                    break

                # Run evaluation for this provider using evaluate function
                results = evaluate(
                    lambda x: x,
                    data=provider_examples,
                    evaluators=[search_accuracy_evaluator],
                    experiment_prefix=f"Search_Battle_{provider}",
                )

                # Try to access results - this will raise the error if results are malformed
                test_scores = [r.get("score", 0) for r in results]

                all_results[provider] = results
                break  # Success - exit retry loop

            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    print(
                        f"❌ Failed to evaluate {provider} after {max_retries} attempts: {str(e)}"
                    )
                else:
                    print(
                        f"Attempt {attempt + 1} failed for {provider}: {str(e)}. Retrying..."
                    )

    print("\nAll done.")
    return all_results


if __name__ == "__main__":
    run_evaluation()
