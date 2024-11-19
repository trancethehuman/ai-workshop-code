import os
from quotientai import QuotientAI
from tracing_example import (
    get_article_summary,
)
from prompts import system_prompt_article_summary
from example_article import invest_ottawa_article
from dotenv import load_dotenv

load_dotenv()

quotient = QuotientAI()


def try_quotient():
    article_text = invest_ottawa_article
    stored_prompt_id = os.getenv("QUOTIENT_PROMPT_ID")

    # List all prompts
    prompts = quotient.prompts.list()
    print("Available prompts:")
    for prompt in prompts:
        print(f"ID: {prompt.id}, Name: {prompt.name}")

    # Check if our stored prompt ID exists
    prompt = None
    if stored_prompt_id:
        try:
            prompt = quotient.prompts.get(stored_prompt_id)
            print(f"\nFound existing prompt with ID: {stored_prompt_id}")
        except Exception as e:
            print(f"\nStored prompt ID not found: {e}")

    # Create new prompt if needed
    if not prompt:
        print("\nCreating new prompt...")
        prompt = quotient.prompts.create(
            name="Article Summary",
            user_prompt=system_prompt_article_summary,
        )
        print(f"Created new prompt with ID: {prompt.id}")
        print("Add this ID to your .env file as QUOTIENT_PROMPT_ID")

    print(prompt)

    summary = get_article_summary(article_text, prompt.user_prompt)
    print("\nSummary using Quotient prompt:", summary)


if __name__ == "__main__":
    try_quotient()
