from exa_py import Exa
from langsmith import traceable
import os
from dotenv import load_dotenv
from openai import OpenAI
from langsmith.wrappers import wrap_openai

load_dotenv()


def setup_client():
    """Initialize and return the Exa client"""
    return Exa(os.getenv("EXA_API_KEY"))


def setup_openai_client():
    """Initialize and return the wrapped OpenAI client"""
    return wrap_openai(OpenAI())


@traceable(name="exa", tags=["search_battle"])
def get_response_exa(query: str) -> dict:
    exa_client = setup_client()
    openai_client = setup_openai_client()

    try:
        # Get search results from Exa
        results = exa_client.search_and_contents(
            query,
            type="neural",
            use_autoprompt=True,
            num_results=5,
            text=True,
            summary=True,
        )

        # Collect sources and their summaries
        sources = []
        summaries = []
        for result in results.results:
            source = {
                "title": result.title,
                "url": result.url,
                "published_date": result.published_date,
                "author": result.author,
            }
            sources.append(source)
            if hasattr(result, "summary"):
                summaries.append(result.summary)

        # If we have summaries, use OpenAI to generate a natural language answer
        if summaries:
            prompt = f"""Based on the following search results, provide a concise and accurate answer to the query: "{query}"

Search Results:
{chr(10).join(f'- {summary}' for summary in summaries)}

Please provide a direct answer based on these search results."""

            completion = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides accurate, concise answers based on search results.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            answer = completion.choices[0].message.content
        else:
            answer = "No relevant information found in search results."

        # Make sure we're returning a string for the output
        if not isinstance(answer, str):
            answer = str(answer)

        response_dict = {
            "output": answer,
            "model": "exa-neural",
            "grounded": True,
            "sources": sources,
            "grounding_info": {
                "request_id": results.request_id
                if hasattr(results, "request_id")
                else None,
                "summaries": summaries,
            },
        }

        return response_dict

    except Exception as e:
        print(f"Debug - Exception type: {type(e)}")
        print(f"Debug - Full error: {str(e)}")
        return {
            "output": f"Error getting Exa response: {str(e)}",
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
    print(f"Response: {result['output']}")
    print(f"Model: {result['model']}")
    print(f"Grounded: {result['grounded']}")

    if result["sources"]:
        print("\nSources:")
        for source in result["sources"]:
            print(f"- {source['title']} ({source['url']})")

    if result["grounding_info"].get("summaries"):
        print("\nSource Summaries:")
        for summary in result["grounding_info"]["summaries"]:
            print(f"- {summary}")
