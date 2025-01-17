from openai import OpenAI
from dotenv import load_dotenv
from langsmith import traceable
import os
from prompts import ARTICLE_GENERATOR_PROMPT

load_dotenv()

client = OpenAI()


def generate_article(subject: str, length: int) -> str:
    """
    Generate an article about a technical subject with specified length.

    Args:
        subject (str): The technical subject to write about
        length (int): Desired length of the article in words

    Returns:
        str: Generated article with HTML formatting
    """

    @traceable(name="article_generator", run_type="llm", tags=[subject])
    def _traced_generate(subject: str, length: int) -> str:
        # Replace placeholders in the prompt template
        prompt = ARTICLE_GENERATOR_PROMPT.replace("{{TECHNICAL_SUBJECT}}", subject)
        prompt = prompt.replace("{{ARTICLE_LENGTH}}", f"{length} words")

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Please generate the article now."},
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content

    return _traced_generate(subject, length)


if __name__ == "__main__":
    # Example usage
    article = generate_article("Quantum Computing", 500)
    print(article)
