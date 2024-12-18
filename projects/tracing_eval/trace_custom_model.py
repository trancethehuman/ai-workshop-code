from openai import OpenAI
from dotenv import load_dotenv
from langsmith import traceable
from example_article import invest_ottawa_article
import os
from prompts import (
    system_prompt_article_summary,
)
import tiktoken
from pydantic import BaseModel

load_dotenv()

# GEMINI MODEL
gemini_client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model_name = "gemini-2.0-flash-exp"


class UsageMetadata(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int


class GeminiResponse(BaseModel):
    result: str
    usage_metadata: UsageMetadata


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(string))


@traceable(
    name=model_name,
    run_type="llm",
    metadata={"ls_provider": "gemini", "ls_model_name": model_name},
)
def get_gemini_response(messages: list) -> GeminiResponse:
    response = gemini_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0,
        max_tokens=2048,
        top_p=1,
    )

    input_tokens = num_tokens_from_string(
        "".join(msg["content"] for msg in messages),
        "cl100k_base",
    )

    output_tokens = num_tokens_from_string(
        response.choices[0].message.content,
        "cl100k_base",
    )

    total_tokens = input_tokens + output_tokens

    return GeminiResponse(
        result=response.choices[0].message.content,
        usage_metadata=UsageMetadata(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        ),
    )


@traceable(name="summarize_article_bla")
def get_article_summary(article_text: str, system_prompt: str):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": article_text},
    ]

    response = get_gemini_response(messages=messages)
    return response.result


if __name__ == "__main__":
    article_text = invest_ottawa_article
    summary = get_article_summary(article_text, system_prompt_article_summary)
    print("Summary by gemini:", summary)
