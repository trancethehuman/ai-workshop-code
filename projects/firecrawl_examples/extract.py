import os
import time
import asyncio
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


class BusinessInfo(BaseModel):
    business_name: str
    business_address: str
    menu_items: str
    operating_hours: str
    phone: str


async def extract_using_scrape_and_llm():
    """
    Extract information using scrape endpoint + LLM approach
    """
    print("Starting scrape + LLM extraction...")
    # First scrape the website
    scrape_response = firecrawl.scrape_url(
        "https://whitscustard.com/locations/granville", params={"formats": ["markdown"]}
    )

    # Then use Groq to extract structured data
    system_message = f"""
    You're an expert at doing data extraction on website content into JSON format. 
    Extract all relevant business information including business name, address, phone, 
    operating hours, and menu items if available.

    Return the data exactly matching this JSON schema:
    {str(BusinessInfo.model_json_schema())}
    """

    completion = groq.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": scrape_response["markdown"]},
        ],
        temperature=0,
        max_tokens=8000,
        response_format={"type": "json_object"},
    )

    result = json.loads(completion.choices[0].message.content)

    # Validate against our Pydantic model
    validated_result = BusinessInfo(**result).model_dump()

    # Save results
    with open("results/scrape_llm_results.txt", "w") as f:
        json.dump(validated_result, f, indent=2)

    print("✓ Scrape + LLM extraction completed")
    return validated_result


async def extract_using_firecrawl_extract():
    """
    Extract information using Firecrawl's new extract endpoint
    """
    print("Starting Firecrawl extract...")
    # Start extraction job
    extract_job = firecrawl.async_extract(
        ["https://whitscustard.com/locations/granville"],
        {
            "prompt": "Extract all business information including name, address, phone number, operating hours, and menu items. If there are no menu items, infer.",
            "schema": BusinessInfo.model_json_schema(),
        },
    )

    print(f"Extract job created with ID: {extract_job['id']}")

    # Poll until job is complete
    while True:
        job_status = firecrawl.get_extract_status(extract_job["id"])
        print(f"Status: {job_status['status']}")
        if job_status["status"] == "completed":
            extract_response = job_status
            break
        await asyncio.sleep(1)  # Use asyncio.sleep instead of time.sleep

    # Save results
    with open("./results/firecrawl_extract_results.txt", "w") as f:
        json.dump(extract_response["data"], f, indent=2)

    print("✓ Firecrawl extraction completed")
    return extract_response["data"]


async def main():
    print("Starting both extraction methods concurrently...")

    # Run both extraction methods concurrently
    scrape_llm_task = asyncio.create_task(extract_using_scrape_and_llm())
    firecrawl_extract_task = asyncio.create_task(extract_using_firecrawl_extract())

    try:
        # Wait for both tasks to complete
        scrape_llm_results, firecrawl_extract_results = await asyncio.gather(
            scrape_llm_task, firecrawl_extract_task
        )

        print("\nBoth extractions completed successfully!")
        print(
            "\nResults saved to results/scrape_llm_results.txt and results/firecrawl_extract_results.txt"
        )

        # Compare results
        print("\nComparison of extracted data:")
        print("\nScrape + LLM approach found:")
        print(json.dumps(scrape_llm_results, indent=2))
        print("\nFirecrawl extract endpoint found:")
        print(json.dumps(firecrawl_extract_results, indent=2))

    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
