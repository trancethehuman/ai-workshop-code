from tavily import TavilyClient
from langsmith import traceable
import os
from dotenv import load_dotenv

load_dotenv()


def setup_client():
    """Initialize and return the Tavily client"""
    return TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@traceable(name="tavily", tags=["search_battle"])
def get_response_tavily(query: str) -> dict:
    client = setup_client()

    try:
        # Execute search with include_answer=True to get the answer field
        response = client.search(
            query=query, search_depth="advanced", include_answer=True
        )

        # Extract sources from results
        sources = [
            {"url": result["url"], "title": result["title"]}
            for result in response.get("results", [])
        ]

        # Make sure we get a string response
        answer = response.get("answer", "No answer provided")
        if not isinstance(answer, str):
            answer = str(answer)

        # Debug print
        print(f"\nTavily Debug - Raw answer: {answer}")

        result_dict = {
            "output": answer,
            "model": "tavily-search",
            "grounded": True,
            "sources": sources,
            "grounding_info": {
                "response_time": response.get("response_time"),
                "follow_up_questions": response.get("follow_up_questions"),
            },
        }

        return result_dict

    except Exception as e:
        print(f"Debug - Exception type: {type(e)}")
        print(f"Debug - Full error: {str(e)}")
        return {
            "output": f"Error getting Tavily response: {str(e)}",
            "model": "tavily-search",
            "grounded": False,
            "sources": [],
            "grounding_info": {},
        }


if __name__ == "__main__":
    # Test query
    query = "Who won the Jake Paul and Mike Tyson fight?"
    result = get_response_tavily(query)

    print(f"\nQuery: {query}")
    print(f"Response: {result['output']}")
    print(f"Model: {result['model']}")
    print(f"Grounded: {result['grounded']}")

    if result["sources"]:
        print("\nSources:")
        for source in result["sources"]:
            print(f"- {source['title']}: {source['url']}")

    if result["grounding_info"].get("follow_up_questions"):
        print("\nFollow-up Questions:")
        for question in result["grounding_info"]["follow_up_questions"]:
            print(f"- {question}")
