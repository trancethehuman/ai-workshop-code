"""
Custom search tool using Tavily API for more powerful web search capabilities.
"""

import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
import logging

from agents import function_tool, RunContextWrapper

# Configure logging
logger = logging.getLogger("tavily_search")

# Load environment variables to get the Tavily API key
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Try importing Tavily client, handle case where it might not be installed
try:
    from tavily import TavilyClient

    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    logger.warning(
        "Tavily Python SDK not found. Run 'pip install tavily-python' to use Tavily search."
    )
except Exception as e:
    TAVILY_AVAILABLE = False
    logger.warning(f"Error initializing Tavily client: {str(e)}")


async def search_tavily(query: str, max_results: int = 5) -> str:
    """
    Internal function to search using the Tavily API.
    """
    from tavily import TavilyClient

    # Initialize Tavily client from environment variable
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    if not tavily_api_key:
        return "Error: TAVILY_API_KEY environment variable not found."

    # Create client instance
    tavily_client = TavilyClient(api_key=tavily_api_key)

    try:
        # Call the Tavily API using the client
        response = tavily_client.search(
            query=query, search_depth="basic", max_results=max_results
        )

        if not response or "results" not in response:
            return f"No results found for query: {query}"

        # Format the results
        results_text = f"Web search results for '{query}':\n\n"

        for i, result in enumerate(response["results"]):
            results_text += f"{i + 1}. {result.get('title', 'No title')}\n"
            results_text += f"   URL: {result.get('url', 'No URL')}\n"
            results_text += f"   {result.get('content', 'No content available')}\n\n"

        return results_text

    except Exception as e:
        return f"Error searching the web: {str(e)}"


@function_tool
async def tavily_search(
    ctx: RunContextWrapper,
    query: str,
    max_results: Optional[int] = None,
) -> str:
    """
    Search the web for information using Tavily search engine.

    Args:
        query: The search query to find information on the web
        max_results: Number of results to return (between 1 and 10)
        search_depth: Depth of search, either "basic" for faster results or "comprehensive" for more thorough search

    Returns:
        Information found on the web related to the query
    """
    # Set the tool name in context
    ctx.context.set_last_tool("tavily_search")

    # Apply defaults inside the function
    if max_results is None:
        max_results = 5

    return await search_tavily(query=query, max_results=max_results)
