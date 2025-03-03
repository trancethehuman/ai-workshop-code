import os
from dotenv import load_dotenv
from litellm import completion

# Load environment variables from .env file
load_dotenv()

# Make sure you have set GOOGLE_API_KEY in your .env file
if not os.getenv("GOOGLE_API_KEY"):
    print("ERROR: GOOGLE_API_KEY not found in environment variables")
    print("Please add it to your .env file")
    exit(1)


def test_gemini():
    try:
        # Call Gemini through LiteLLM
        response = completion(
            model="gemini/gemini-2.0-flash-lite",
            messages=[
                {
                    "role": "user",
                    "content": "Write a short paragraph about Jeff Bezos and his approach to business",
                }
            ],
        )

        # Print the response
        print("\nSuccessful Gemini API call!")
        print("=" * 40)
        print(f"Model: {response.model}")
        print(f"Response: {response.choices[0].message.content}")
        print("=" * 40)

        # Print usage information if available
        if hasattr(response, "usage") and response.usage:
            print("\nUsage information:")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Completion tokens: {response.usage.completion_tokens}")
            print(f"Total tokens: {response.usage.total_tokens}")

        return True
    except Exception as e:
        print(f"\nError calling Gemini API: {e}")
        return False


if __name__ == "__main__":
    print("Testing Gemini API integration...")
    test_gemini()
