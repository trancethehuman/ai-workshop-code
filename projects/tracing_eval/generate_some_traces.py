import openai
import json
from prompts import (
    system_prompt_article_summary,
    system_prompt_article_summary_pirate,
    system_prompt_article_summary_second_grade,
)
from example_article import invest_ottawa_article
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from typing import List, Dict

from tracing_example import get_article_summary


if __name__ == "__main__":
    article_text = invest_ottawa_article
    prompts = [
        system_prompt_article_summary,
        system_prompt_article_summary_pirate,
        system_prompt_article_summary_second_grade,
    ]

    for prompt in prompts:
        summary = get_article_summary(article_text, prompt)
        print(f"\nSummary using prompt {prompt[:50]}...:", summary)
    print("Summary:", summary)
