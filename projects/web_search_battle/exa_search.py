from exa_py import Exa
from langsmith import traceable
import os
from dotenv import load_dotenv

load_dotenv()


def setup_client():
    """Initialize and return the Exa client"""
    return Exa(os.getenv("EXA_API_KEY"))


@traceable(name="exa")
def get_response_exa(query: str) -> dict:
    client = setup_client()

    try:
        results = client.search_and_contents(
            query,
            type="neural",
            use_autoprompt=True,
            num_results=5,
            text=True,
        )

        # Extract relevant information from results
        sources = []
        for result in results.results:
            source = {
                "title": result.title,
                "url": result.url,
                "published_date": result.published_date,
                "author": result.author,
            }
            sources.append(source)

        return {
            "response": results.autoprompt_string
            if hasattr(results, "autoprompt_string")
            else "",
            "model": "exa-neural",
            "grounded": True,
            "sources": sources,
            "grounding_info": {
                "request_id": results.request_id
                if hasattr(results, "request_id")
                else None
            },
        }

    except Exception as e:
        print(f"Debug - Exception type: {type(e)}")
        print(f"Debug - Full error: {str(e)}")
        return {
            "response": f"Error getting Exa response: {str(e)}",
            "model": "exa-neural",
            "grounded": False,
            "sources": [],
            "grounding_info": {},
        }


if __name__ == "__main__":
    # Test query
    query = "Who won the Jake Paul and Mike Tyson fight?"
    result = get_response_exa(query)

    print(f"\nQuery: {query}")
    print(f"Response: {result['response']}")
    print(f"Model: {result['model']}")
    print(f"Grounded: {result['grounded']}")

    if result["sources"]:
        print("\nSources:")
        for source in result["sources"]:
            print(f"- {source['title']} ({source['url']})")
