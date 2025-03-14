import os
from typing import Any, Dict
from agents import RunContextWrapper, function_tool
from dotenv import load_dotenv
import requests
from agent_tools.utils.linkedin import parse_linkedin_profile
from models.sales import SalesContext

load_dotenv()

scraper_api_key = os.environ.get("SCRAPER_API_KEY")


@function_tool
def extract_linkedin_profile(
    wrapper: RunContextWrapper[SalesContext], linkedin_url: str
) -> Dict[str, Any]:
    """Extract profile data from a LinkedIn URL"""
    print("Start scraping & extracting LinkedIn")

    payload = {
        "api_key": scraper_api_key,
        "url": linkedin_url,
        "output_format": "markdown",
    }
    response = requests.get(
        "https://api.scraperapi.com/",
        params=payload,
    )

    page_markdown = response.text

    # Extract the user's profile from the response
    profile_data = parse_linkedin_profile(page_markdown)

    # Update the context with the extracted profile data
    wrapper.context["profile_data"] = profile_data

    print("Finished LinkedIn extration.")

    return profile_data
