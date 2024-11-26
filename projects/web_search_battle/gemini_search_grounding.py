import google.generativeai as genai
from langsmith import traceable
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def setup_model():
    """Initialize and return the Gemini model"""
    return genai.GenerativeModel("models/gemini-1.5-flash")


@traceable(name="gemini", tags=["search_battle"])
def get_response_google_grounding(
    query: str, dynamic_threshold: Optional[float] = None
) -> str:
    model = setup_model()

    # Configure grounding tools
    if dynamic_threshold is not None:
        tools = {
            "google_search_retrieval": {
                "dynamic_retrieval_config": {
                    "mode": "MODE_DYNAMIC",
                    "dynamic_threshold": dynamic_threshold,
                }
            }
        }
    else:
        tools = "google_search_retrieval"

    try:
        response = model.generate_content(contents=query, tools=tools)

        sources = []
        grounding_info = {}

        # Extract grounding metadata from the first candidate
        if (
            hasattr(response, "candidates")
            and response.candidates
            and hasattr(response.candidates[0], "grounding_metadata")
        ):
            metadata = response.candidates[0].grounding_metadata

            # Get grounding chunks (sources)
            if hasattr(metadata, "grounding_chunks"):
                for chunk in metadata.grounding_chunks:
                    if hasattr(chunk, "web") and hasattr(chunk.web, "uri"):
                        sources.append(chunk.web.uri)

            # Get search entry point if available
            if hasattr(metadata, "search_entry_point"):
                grounding_info["search_suggestion"] = (
                    metadata.search_entry_point.rendered_content
                )

            # Get supporting segments if available
            if hasattr(metadata, "grounding_supports"):
                grounding_info["supports"] = metadata.grounding_supports

        return {
            "output": response.text,
            "grounded": len(sources) > 0,
            "sources": list(set(sources)),  # Remove duplicates
            "grounding_info": grounding_info,
        }

    except Exception as e:
        print(f"Debug - Exception type: {type(e)}")
        print(f"Debug - Full error: {str(e)}")
        return {
            "output": f"Error getting grounded response: {str(e)}",
            "grounded": False,
            "sources": [],
            "grounding_info": {},
        }


if __name__ == "__main__":
    # Use a query that's more likely to trigger grounding
    query = "Who won the Jake Paul and Mike Tyson fight"
    result = get_response_google_grounding(query)

    print(f"\nQuery: {query}")
    print(f"Response: {result['output']}")
    print(f"Grounded: {result['grounded']}")

    if result["sources"]:
        print("\nSources:")
        for source in result["sources"]:
            print(f"- {source}")

    if result["grounding_info"]:
        print("\nGrounding Info:")
        if "search_suggestion" in result["grounding_info"]:
            print("\nSearch Suggestion:")
            print(result["grounding_info"]["search_suggestion"])
        if "supports" in result["grounding_info"]:
            print("\nSupporting Segments:")
            print(result["grounding_info"]["supports"])
