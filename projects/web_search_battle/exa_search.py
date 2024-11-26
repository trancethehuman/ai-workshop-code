from exa_py import Exa
from langsmith import traceable
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
from pydantic import BaseModel
from langsmith.wrappers import wrap_openai


load_dotenv()


def setup_client():
    """Initialize and return the Exa client"""
    return Exa(os.getenv("EXA_API_KEY"))


def setup_openai_client():
    """Initialize and return the wrapped OpenAI client"""
    return wrap_openai(OpenAI())


def setup_gemini_client():
    """Initialize and return the Gemini client"""
    return OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )


def format_date(date_str: str) -> str:
    """Format date string to be more readable"""
    try:
        date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return date.strftime("%B %d, %Y")
    except:
        return date_str


@traceable(name="exa", tags=["search_battle"])
def get_response_exa(query: str) -> dict:
    exa_client = setup_client()
    openai_client = setup_openai_client()
    model_name = "gpt-4o-mini"

    try:
        # Get search results from Exa
        results = exa_client.search_and_contents(
            query,
            type="neural",
            use_autoprompt=True,
            num_results=5,
            text=True,
        )

        # Collect sources and their content with dates
        sources = []
        search_results = []
        for result in results.results:
            source = {
                "title": result.title,
                "url": result.url,
                "published_date": result.published_date,
                "author": result.author,
            }
            sources.append(source)

            if hasattr(result, "text"):
                formatted_date = (
                    format_date(result.published_date)
                    if result.published_date
                    else "Date unknown"
                )
                search_results.append({"text": result.text, "date": formatted_date})

        # If we have text content, use Gemini to generate a natural language answer
        if search_results:
            # Sort results by date, most recent first
            search_results.sort(
                key=lambda x: x["date"] if x["date"] != "Date unknown" else "",
                reverse=True,
            )

            prompt = f"""Based on the following search results (sorted by date), provide a concise and accurate answer to the query: "{query}"

Search Results:
{chr(10).join(f'[{result["date"]}] - {result["text"]}' for result in search_results)}

Please provide a direct answer based on these search results, prioritizing the most recent information when relevant."""

            completion = openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides accurate, concise answers based on search results. When information conflicts, prefer more recent sources.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=2048,
                top_p=1,
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
                "content": [r["text"] for r in search_results],
                "dates": [r["date"] for r in search_results],
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
    query = "Who is the president of the US in 2025?"
    result = get_response_exa(query)

    print(f"\nQuery: {query}")
    print(f"Response: {result['output']}")
    print(f"Model: {result['model']}")
    print(f"Grounded: {result['grounded']}")

    if result["sources"]:
        print("\nSources:")
        for source in result["sources"]:
            print(
                f"- {source['title']} ({source['url']}) - Published: {source['published_date']}"
            )

    if result["grounding_info"].get("content"):
        print("\nSource Content with Dates:")
        for content, date in zip(
            result["grounding_info"]["content"], result["grounding_info"]["dates"]
        ):
            print(f"[{date}] - {content[:200]}...")  # Print first 200 chars of content
