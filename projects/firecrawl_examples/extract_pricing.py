import os
import json
import asyncio
import time
from pathlib import Path
from datetime import datetime
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import Any, Optional, List
from dotenv import load_dotenv
import platform

load_dotenv()

# Initialize Firecrawl client
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
firecrawl = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

# Create results directory
RESULTS_DIR = Path("pricing_results")
RESULTS_DIR.mkdir(exist_ok=True)


class ModelPricing(BaseModel):
    model_name: str
    input_price: Optional[float] = Field(description="Price per 1K input tokens in USD")
    output_price: Optional[float] = Field(
        description="Price per 1K output tokens in USD"
    )
    additional_details: Optional[str] = Field(
        description="Any additional pricing details or notes"
    )


class CompanyPricing(BaseModel):
    company_name: str
    models: List[ModelPricing]
    last_updated: Optional[str] = Field(
        description="When this pricing was last updated according to the website"
    )


# List of companies to crawl
COMPANIES = [
    {"url": "https://openai.com/*", "name": "OpenAI"},
    {"url": "https://www.deepseek.com/*", "name": "DeepSeek"},
    {"url": "https://ai.google.dev/*", "name": "Google Gemini"},
]


async def extract_pricing_individual():
    """Extract pricing information for each company individually"""
    print("\nStarting individual extractions...")
    start_time = time.time()

    try:
        tasks = [extract_pricing_for_company(company) for company in COMPANIES]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine all results
        combined_results = {
            "timestamp": datetime.now().isoformat(),
            "companies": [r for r in results if r is not None],
            "extraction_method": "individual",
            "execution_time": time.time() - start_time,
        }

        # Save combined results
        with open(RESULTS_DIR / "individual_extraction_results.json", "w") as f:
            json.dump(combined_results, f, indent=2)

        print(
            f"\n✓ Individual extraction completed in {combined_results['execution_time']:.2f} seconds"
        )
        return combined_results

    except Exception as e:
        print(f"\nAn error occurred in individual extraction: {str(e)}")
        return None


async def extract_pricing_batch():
    """Extract pricing information for all companies in one batch"""
    print("\nStarting batch extraction...")
    start_time = time.time()

    try:
        # Prepare URLs and create batch job
        urls = [company["url"] for company in COMPANIES]
        extract_job = firecrawl.async_extract(
            urls,
            {
                "prompt": """Extract all AI model pricing information from this company's website. 
                Include model names, input prices (per 1K tokens), output prices (per 1K tokens), 
                and any additional pricing details. Also note when the pricing was last updated if available.""",
                "schema": CompanyPricing.model_json_schema(),
            },
        )

        print(f"Batch extract job created with ID: {extract_job['id']}")

        # Poll until job is complete
        while True:
            job_status = firecrawl.get_extract_status(extract_job["id"])
            print(f"Batch status: {job_status['status']}")
            if job_status["status"] == "completed":
                extract_response = job_status
                break
            await asyncio.sleep(2)

        # Process and save results
        execution_time = time.time() - start_time
        combined_results = {
            "timestamp": datetime.now().isoformat(),
            "companies": extract_response["data"],
            "extraction_method": "batch",
            "execution_time": execution_time,
        }

        # Save results
        with open(RESULTS_DIR / "batch_extraction_results.json", "w") as f:
            json.dump(combined_results, f, indent=2)

        print(f"\n✓ Batch extraction completed in {execution_time:.2f} seconds")
        return combined_results

    except Exception as e:
        print(f"\nAn error occurred in batch extraction: {str(e)}")
        return None


async def extract_pricing_for_company(company):
    """Extract pricing information for a single company"""
    print(f"Starting extraction for {company['name']}...")

    try:
        # Start extraction job
        extract_job = firecrawl.async_extract(
            [company["url"]],
            {
                "prompt": """Extract all AI model pricing information from this company's website. 
                Include model names, input prices (per 1K tokens), output prices (per 1K tokens), 
                and any additional pricing details. Also note when the pricing was last updated if available.""",
                "schema": CompanyPricing.model_json_schema(),
            },
        )

        print(f"Extract job created for {company['name']} with ID: {extract_job['id']}")

        # Poll until job is complete
        while True:
            job_status = firecrawl.get_extract_status(extract_job["id"])
            print(f"Status for {company['name']}: {job_status['status']}")
            if job_status["status"] == "completed":
                extract_response = job_status
                break
            await asyncio.sleep(2)

        # Save individual company result
        result_file = RESULTS_DIR / f"{company['name'].lower()}_pricing.json"
        with open(result_file, "w") as f:
            json.dump(extract_response["data"], f, indent=2)

        print(f"✓ Extraction completed for {company['name']}")
        return extract_response["data"]

    except Exception as e:
        print(f"Error extracting data for {company['name']}: {str(e)}")
        return None


async def main():
    print("Starting pricing extraction comparison...")

    try:
        # Run both methods concurrently
        individual_task = asyncio.create_task(extract_pricing_individual())
        batch_task = asyncio.create_task(extract_pricing_batch())

        # Wait for both to complete
        individual_results, batch_results = await asyncio.gather(
            individual_task, batch_task
        )

        # Compare results
        print("\nComparison of extraction methods:")
        if individual_results and batch_results:
            individual_time = individual_results["execution_time"]
            batch_time = batch_results["execution_time"]
            time_difference = abs(individual_time - batch_time)
            faster_method = "batch" if batch_time < individual_time else "individual"

            print(f"\nIndividual extraction time: {individual_time:.2f} seconds")
            print(f"Batch extraction time: {batch_time:.2f} seconds")
            print(
                f"\n{faster_method.capitalize()} extraction was faster by {time_difference:.2f} seconds"
            )

            # Create performance comparison data
            performance_data = {
                "timestamp": datetime.now().isoformat(),
                "comparison": {
                    "individual_time": individual_time,
                    "batch_time": batch_time,
                    "time_difference": time_difference,
                    "faster_method": faster_method,
                    "speedup_factor": max(individual_time, batch_time)
                    / min(individual_time, batch_time),
                },
                "urls_processed": len(COMPANIES),
                "system_info": {
                    "python_version": platform.python_version(),
                    "os": platform.system(),
                    "firecrawl_version": firecrawl.__version__,
                },
            }

            # Save performance comparison
            with open(RESULTS_DIR / "performance_comparison.json", "w") as f:
                json.dump(performance_data, f, indent=2)

        print(f"\nAll results saved in {RESULTS_DIR}")

    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
