import openai
import json
from prompts import (
    system_prompt_article_summary,
    system_prompt_what_companies_were_mentioned,
    system_prompt_json_companies,
)
from example_article import invest_ottawa_article
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from typing import List, Dict

from dotenv import load_dotenv

load_dotenv()

client = wrap_openai(openai.Client())


@traceable(name="summarize_article")
def get_article_summary(article_text: str, system_prompt: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": article_text},
        ],
        temperature=0,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].message.content


@traceable(name="get_ottawa_companies")
def get_ottawa_companies(article_text: str, system_prompt: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": article_text},
        ],
        temperature=0,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].message.content


@traceable(name="convert_companies_to_json")
def convert_companies_to_json(
    companies_text: str, system_prompt: str
) -> List[Dict[str, str]]:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": companies_text},
        ],
        temperature=0,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content


@traceable(name="get_companies_json")
def get_companies_json(article_text: str) -> List[Dict[str, str]]:
    companies_list = get_ottawa_companies(
        article_text, system_prompt_what_companies_were_mentioned
    )
    companies_json = convert_companies_to_json(
        companies_list, system_prompt_json_companies
    )
    return json.loads(companies_json)


if __name__ == "__main__":
    article_text = invest_ottawa_article
    summary = get_article_summary(article_text, system_prompt_article_summary)
    print("Summary:", summary)

    companies_json = get_companies_json(article_text)
    print("\nCompanies mentioned (JSON format):", json.dumps(companies_json, indent=2))
