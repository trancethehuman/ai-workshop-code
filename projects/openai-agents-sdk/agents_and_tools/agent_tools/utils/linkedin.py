import json
import logging
import os
from openai import OpenAI
from schemas.linkedin_schema import LINKEDIN_PROFILE_SCHEMA

# Initialize OpenAI client
openai_api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)


def parse_linkedin_profile(markdown_content: str):
    """Extract structured data from LinkedIn profile HTML content using OpenAI API"""
    logging.info("Starting LinkedIn profile structured output extraction")
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": "You're an expert at looking at a person's LinkedIn page and extract out relevant information.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": markdown_content}],
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "linkedin_profile",
                "strict": True,
                "schema": LINKEDIN_PROFILE_SCHEMA,
            }
        },
        reasoning={},
        tools=[],
        temperature=0.5,
        top_p=1,
    )

    return json.loads(response.output_text)
