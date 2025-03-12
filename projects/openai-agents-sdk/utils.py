import os
import logging
from dotenv import load_dotenv
from agents import set_default_openai_key


# Initialize logging - set to WARNING to suppress most logs
def setup_logging():
    """Configure logging for the application"""
    # Set to WARNING level to suppress INFO logs
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger("founder_agent")


# Load environment variables and set up API keys
def load_api_keys():
    """Load environment variables and set up API keys"""
    load_dotenv()

    # Get and set OpenAI API key
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    set_default_openai_key(openai_api_key)

    # Check for Tavily API key
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    if not tavily_api_key:
        # Use print instead of logging to ensure visibility
        print(
            "Warning: TAVILY_API_KEY environment variable is not set. Web search will not work."
        )

    return {"openai_api_key": openai_api_key, "tavily_api_key": tavily_api_key}


# Format search results helper
def format_document_length(text):
    """Add document length indicator to help assess completeness"""
    doc_length = len(text.split())

    if doc_length < 50:
        return "(very brief)"
    elif doc_length > 200:
        return "(detailed)"
    return ""
