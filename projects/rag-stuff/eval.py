from typing import List
from quotientai import QuotientAI
import os

# Initialize the Quotient logger correctly
quotient = QuotientAI(api_key=os.getenv("QUOTIENT_API_KEY"))
quotient_logger = quotient.logger.init(
    app_name="founder-tribune",
    environment="dev",
    tags={"model": "gpt-4o-mini", "feature": "customer-support"},
    hallucination_detection=True,
    hallucination_detection_sample_rate=1.0,
)


# Function to evaluate model outputs for hallucinations
def evaluate_generation(question: str, model_output: str, documents: List[str]):
    """Log the generation to Quotient for hallucination detection and return the response"""
    print(f"Evaluating generation for hallucinations...")

    # Format documents as list of strings - Quotient expects a list of document texts
    doc_texts = documents

    # Log to Quotient with the correct format
    try:
        response = quotient_logger.log(
            user_query=question, model_output=model_output, documents=doc_texts
        )

        # Check if we have a hallucination response
        if hasattr(response, "hallucination") and response.hallucination:
            print(
                f"⚠️ HALLUCINATION DETECTED: {response.hallucination.score:.2f} confidence"
            )
            if response.hallucination.spans:
                print("Hallucinated content:")
                for span in response.hallucination.spans:
                    print(f"  - {span.text}")
        else:
            print("✓ No hallucinations detected")

        return response

    except Exception as e:
        print(f"Error logging to Quotient: {e}")
        # Return None to indicate logging failed
        return None


# Function to print evaluation results
def print_evaluation_results(results, max_length=250):
    """Print the evaluation results with more visual formatting and shorter answers"""

    print("\n\n" + "✨" * 30)
    print("📊  EVALUATION RESULTS SUMMARY  📊")
    print("✨" * 30)

    for idx, result in enumerate(results):
        # Display question with number
        print(f"\n\n📝 QUESTION #{idx + 1}: {result.question}")
        print("=" * 80)

        # Show document count
        doc_count = len(result.documents)
        print(f"📚 Retrieved {doc_count} documents")

        # Show model responses
        for model, answer in result.model_responses.items():
            # Create a cleaner model name
            model_name = model.split("/")[-1]
            print(f"\n🤖 MODEL: {model_name}")
            print("-" * 60)

            # Truncate answers more aggressively
            if len(answer) > max_length:
                # Split on sentence boundaries if possible
                sentence_end = answer[:max_length].rfind(".")
                if sentence_end > max_length // 2:
                    # Found a good sentence break
                    truncated_answer = answer[: sentence_end + 1] + " [...truncated...]"
                else:
                    # Just cut at max_length
                    truncated_answer = answer[:max_length] + " [...truncated...]"

                print(truncated_answer)
            else:
                print(answer)

            print("-" * 60)

        # Add separator between questions
        if idx < len(results) - 1:
            print("\n" + "•" * 80)

    print("\n" + "🏁" * 20)
    print("End of results")
    print("🏁" * 20 + "\n")
