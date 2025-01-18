from openai import OpenAI
from dotenv import load_dotenv
from langsmith.schemas import Example
from eval_utils import (
    read_articles_from_directory,
    create_evaluation_dataset,
    format_evaluation_results,
    print_evaluation_tables,
    run_evaluators,
)
from pydantic import BaseModel
from typing import List

load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI()

# Model constant
EVAL_MODEL = "gpt-4o-mini"


class OpeningEvaluation(BaseModel):
    score: float
    justification: str
    improvement_suggestions: List[str]


class WritingEvaluation(BaseModel):
    score: float
    justification: str
    improvement_suggestions: List[str]


class TechnicalEvaluation(BaseModel):
    score: float
    justification: str
    improvement_suggestions: List[str]


class ReferencesEvaluation(BaseModel):
    score: float
    justification: str
    improvement_suggestions: List[str]


def opening_effectiveness_evaluator(example: Example) -> dict:
    """Evaluate the article's opening effectiveness"""
    evaluation_prompt = """You are an expert editor evaluating an article about {topic}.
    Score the article's opening effectiveness (0-5):
    - Does it explain why the article is important to read?
    - Does it establish author credibility/expertise?
    - Does it hook the reader and provide clear context?
    
    Provide your evaluation in JSON format with:
    - score (float between 0-5)
    - justification (string explaining the score)
    - improvement_suggestions (array of strings with specific improvements needed)
    
    Article to evaluate:
    {article}"""

    topic = example.inputs.get("topic", "technology")
    article = example.inputs.get("article", "")

    completion = openai_client.chat.completions.create(
        model=EVAL_MODEL,
        messages=[
            {
                "role": "system",
                "content": evaluation_prompt.format(topic=topic, article=article),
            }
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    eval_result = OpeningEvaluation.model_validate_json(
        completion.choices[0].message.content
    )

    return {
        "score": eval_result.score / 5,  # Normalize to 0-1 range
        "comment": eval_result.justification,
        "evaluator_info": {
            "opening_score": eval_result.score,
            "improvement_suggestions": ", ".join(eval_result.improvement_suggestions),
        },
        "key": "opening_effectiveness",
    }


def writing_quality_evaluator(example: Example) -> dict:
    """Evaluate the article's writing quality"""
    evaluation_prompt = """You are an expert editor evaluating an article about {topic}.
    Score the article's writing quality (0-5):
    - Is it concise without filler words?
    - Are paragraphs and sentences appropriately sized?
    - Does it avoid overused LLM phrases (like "let's dive in", "let's explore", "dwelve into")?
    - Is the writing clear and engaging?
    
    Provide your evaluation in JSON format with:
    - score (float between 0-5)
    - justification (string explaining the score)
    - improvement_suggestions (array of strings with specific improvements needed)
    
    Article to evaluate:
    {article}"""

    topic = example.inputs.get("topic", "technology")
    article = example.inputs.get("article", "")

    completion = openai_client.chat.completions.create(
        model=EVAL_MODEL,
        messages=[
            {
                "role": "system",
                "content": evaluation_prompt.format(topic=topic, article=article),
            }
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    eval_result = WritingEvaluation.model_validate_json(
        completion.choices[0].message.content
    )

    return {
        "score": eval_result.score / 5,  # Normalize to 0-1 range
        "comment": eval_result.justification,
        "evaluator_info": {
            "writing_score": eval_result.score,
            "improvement_suggestions": ", ".join(eval_result.improvement_suggestions),
        },
        "key": "writing_quality",
    }


def technical_presentation_evaluator(example: Example) -> dict:
    """Evaluate the article's technical presentation"""
    evaluation_prompt = """You are an expert editor evaluating an article about {topic}.
    Score the article's technical presentation (0-5):
    - Are technical concepts clearly explained?
    - Is code (if present) simple to understand?
    - Are examples and analogies used effectively?
    - Is technical jargon properly explained?
    
    Provide your evaluation in JSON format with:
    - score (float between 0-5)
    - justification (string explaining the score)
    - improvement_suggestions (array of strings with specific improvements needed)
    
    Article to evaluate:
    {article}"""

    topic = example.inputs.get("topic", "technology")
    article = example.inputs.get("article", "")

    completion = openai_client.chat.completions.create(
        model=EVAL_MODEL,
        messages=[
            {
                "role": "system",
                "content": evaluation_prompt.format(topic=topic, article=article),
            }
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    eval_result = TechnicalEvaluation.model_validate_json(
        completion.choices[0].message.content
    )

    return {
        "score": eval_result.score / 5,  # Normalize to 0-1 range
        "comment": eval_result.justification,
        "evaluator_info": {
            "technical_score": eval_result.score,
            "improvement_suggestions": ", ".join(eval_result.improvement_suggestions),
        },
        "key": "technical_presentation",
    }


def references_evaluator(example: Example) -> dict:
    """Evaluate the article's references and support"""
    evaluation_prompt = """You are an expert editor evaluating an article about {topic}.
    Score the article's references and support (0-5):
    - Are references or sources included?
    - Are claims properly supported with evidence?
    - Are external resources cited when appropriate?
    - Is there a good balance of facts and explanations?
    
    Provide your evaluation in JSON format with:
    - score (float between 0-5)
    - justification (string explaining the score)
    - improvement_suggestions (array of strings with specific improvements needed)
    
    Article to evaluate:
    {article}"""

    topic = example.inputs.get("topic", "technology")
    article = example.inputs.get("article", "")

    completion = openai_client.chat.completions.create(
        model=EVAL_MODEL,
        messages=[
            {
                "role": "system",
                "content": evaluation_prompt.format(topic=topic, article=article),
            }
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    eval_result = ReferencesEvaluation.model_validate_json(
        completion.choices[0].message.content
    )

    return {
        "score": eval_result.score / 5,  # Normalize to 0-1 range
        "comment": eval_result.justification,
        "evaluator_info": {
            "references_score": eval_result.score,
            "improvement_suggestions": ", ".join(eval_result.improvement_suggestions),
        },
        "key": "references",
    }


def run_evaluation():
    """Run the complete evaluation process"""
    print("Reading articles...")
    articles = read_articles_from_directory()

    if not articles:
        print("No articles found in the generated_articles directory!")
        return

    print(f"\nFound {len(articles)} articles to evaluate")

    print("\nCreating evaluation dataset...")
    dataset = create_evaluation_dataset(articles)

    print("\nRunning evaluations...")
    evaluators = [
        opening_effectiveness_evaluator,
        writing_quality_evaluator,
        technical_presentation_evaluator,
        references_evaluator,
    ]
    results = run_evaluators(dataset.name, evaluators)

    print("\nEvaluation complete! Results are available in LangSmith UI")

    # Format and print results
    table_data, headers = format_evaluation_results(results)
    print_evaluation_tables(table_data, headers)

    return results


if __name__ == "__main__":
    run_evaluation()
