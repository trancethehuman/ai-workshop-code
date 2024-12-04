import os
import asyncio
from firecrawl import FirecrawlApp
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


async def check_batch_status(crawler, job_id):
    """Poll the batch job status until completion"""
    while True:
        status = crawler.check_batch_scrape_status(job_id)
        if status["status"] == "completed":
            return status["data"]
        elif status["status"] == "failed":
            raise Exception(f"Batch job failed: {status.get('error', 'Unknown error')}")

        print(
            f"Status: {status['status']}, Completed: {status.get('completed', 0)}/{status.get('total', '?')}"
        )
        await asyncio.sleep(5)  # Wait 5 seconds before checking again


async def main():
    try:
        # URLs to scrape
        urls = [
            "https://boards.greenhouse.io/anthropic/jobs/4406493008",
            "https://boards.greenhouse.io/anthropic/jobs/4104496008",
            "https://boards.greenhouse.io/anthropic/jobs/4117878008",
            "https://boards.greenhouse.io/anthropic/jobs/4143973008",
            "https://boards.greenhouse.io/anthropic/jobs/4379027008",
            "https://boards.greenhouse.io/anthropic/jobs/4138859008",
        ]

        # Initialize Firecrawl
        firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        if not firecrawl_api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable not set")

        crawler = FirecrawlApp(api_key=firecrawl_api_key)

        # Configure extraction schema
        extraction_params = {
            "formats": ["extract"],
            "extract": {
                "prompt": """Extract the following information from the job posting:
                    1. Job title
                    2. Required skills and technologies (as a list)
                    3. Job description summary (brief, 2-3 sentences)
                    4. Required experience (years and relevant background)
                    5. Location/remote status
                    6. Salary range (if available)""",
                "schema": {
                    "type": "object",
                    "properties": {
                        "job_title": {"type": "string"},
                        "skills": {"type": "array", "items": {"type": "string"}},
                        "description_summary": {"type": "string"},
                        "required_experience": {"type": "string"},
                        "location": {"type": "string"},
                        "salary_range": {"type": "string", "nullable": True},
                    },
                    "required": [
                        "job_title",
                        "skills",
                        "description_summary",
                        "required_experience",
                        "location",
                    ],
                },
            },
        }

        # Start batch scrape
        print("\nStarting batch scrape...")
        batch_job = crawler.async_batch_scrape_urls(urls, extraction_params)
        print(f"Batch job ID: {batch_job['id']}")

        # Poll for results
        print("\nWaiting for results...")
        results = await check_batch_status(crawler, batch_job["id"])

        # Process and save results
        print("\nProcessing results...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"job_scrape_results_{timestamp}.txt"

        with open(output_file, "w") as f:
            for result in results:
                if "extract" in result:
                    job_info = result["extract"]
                    output = f"""
Job Posting:
-----------
Title: {job_info['job_title']}
Location: {job_info['location']}
Skills: {', '.join(job_info['skills'])}
Experience: {job_info['required_experience']}
Salary Range: {job_info.get('salary_range', 'Not specified')}
Summary: {job_info['description_summary']}
                    """
                    print(output)
                    f.write(output + "\n")

        print(f"\nResults saved to {output_file}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
