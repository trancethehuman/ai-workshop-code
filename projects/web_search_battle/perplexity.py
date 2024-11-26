from openai import OpenAI
from langsmith import traceable
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

model_name = "llama-3.1-sonar-small-128k-online"


def setup_client():
    """Initialize and return the Perplexity client"""
    return OpenAI(
        api_key=os.getenv("PERPLEXITY_API_KEY"), base_url="https://api.perplexity.ai"
    )


@traceable(name="perplexity", tags=["search_battle"])
def get_response_perplexity(query: str) -> dict:
    client = setup_client()

    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant. Please provide accurate and up-to-date information based on online sources.",
        },
        {"role": "user", "content": query},
    ]

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
        )

        citations = response.citations if hasattr(response, "citations") else []

        return {
            "output": response.choices[0].message.content,
            "model": model_name,
            "grounded": True,
            "sources": citations,
            "grounding_info": {},
        }

    except Exception as e:
        print(f"Debug - Exception type: {type(e)}")
        print(f"Debug - Full error: {str(e)}")
        return {
            "output": f"Error getting Perplexity response: {str(e)}",
            "model": model_name,
            "grounded": False,
            "sources": [],
            "grounding_info": {},
        }


if __name__ == "__main__":
    # Test query
    query = "Who won the Jake Paul and Mike Tyson fight?"
    result = get_response_perplexity(query)

    print(f"\nQuery: {query}")
    print(f"Response: {result['output']}")
    print(f"Model: {result['model']}")
    print(f"Grounded: {result['grounded']}")

    if result["sources"]:
        print("\nSources:")
        for source in result["sources"]:
            print(f"- {source}")
