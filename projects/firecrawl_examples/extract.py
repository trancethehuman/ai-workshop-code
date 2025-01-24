import os
import time
from firecrawl import FirecrawlApp
from groq import Groq
import json
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
import firecrawl

print(f"Using Firecrawl version: {firecrawl.__version__}")

load_dotenv()

# Initialize clients
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

firecrawl = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
groq = Groq(api_key=GROQ_API_KEY)

# Create results directory if it doesn't exist
Path("results").mkdir(exist_ok=True)


# Define the schema using Pydantic
class BusinessAddress(BaseModel):
    street: str
    city: str
    zip_code: str


class MenuItem(BaseModel):
    item_name: str
    item_description: str


class OperatingHours(BaseModel):
    day: str
    time: str


class BusinessInfo(BaseModel):
    business_name: str
    business_address: str
    menu_items: str
    operating_hours: str
    phone: str


# @title Define helper functions
def extract_using_scrape_and_llm():
    """
    Extract information using scrape endpoint + LLM approach
    """
    # First scrape the website
    scrape_response = firecrawl.scrape_url(
        "https://whitscustard.com/locations/granville", params={"formats": ["markdown"]}
    )

    # Then use Groq to extract structured data
    system_message = """
    You're an expert at doing data extraction on website content into JSON format. 
    Extract all relevant business information including business name, address, phone, 
    operating hours, and menu items if available.
    """

    completion = groq.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": scrape_response["markdown"]},
        ],
        temperature=0,
        max_tokens=8000,
        response_format={"type": "json_object"},
    )

    # Save results
    with open("results/scrape_llm_results.txt", "w") as f:
        f.write(completion.choices[0].message.content)

    return json.loads(completion.choices[0].message.content)


def extract_using_firecrawl_extract():
    """
    Extract information using Firecrawl's new extract endpoint
    """
    # Start extraction job
    extract_job = firecrawl.async_extract(
        ["https://whitscustard.com/locations/granville"],
        {
            "prompt": "Extract all business information including name, address, phone number, operating hours, and menu items if available.",
            "schema": BusinessInfo.model_json_schema(),
        },
    )

    print(extract_job)

    # Poll until job is complete
    while True:
        job_status = firecrawl.get_extract_status(extract_job["id"])
        print(job_status)
        if job_status["status"] == "completed":
            extract_response = job_status
            break
        time.sleep(1)  # Wait 1 second before polling again

    # Save results
    with open("results/firecrawl_extract_results.txt", "w") as f:
        json.dump(extract_response["data"], f, indent=2)

    return extract_response["data"]


def main():
    print("Extracting using scrape + LLM approach...")
    scrape_llm_results = extract_using_scrape_and_llm()
    print("Results saved to results/scrape_llm_results.txt")

    print("\nExtracting using Firecrawl extract endpoint...")
    firecrawl_extract_results = extract_using_firecrawl_extract()
    print("Results saved to results/firecrawl_extract_results.txt")

    # Compare results
    print("\nComparison of extracted data:")
    print("\nScrape + LLM approach found:")
    print(json.dumps(scrape_llm_results, indent=2))
    print("\nFirecrawl extract endpoint found:")
    print(json.dumps(firecrawl_extract_results, indent=2))


if __name__ == "__main__":
    main()
