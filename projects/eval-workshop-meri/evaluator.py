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

load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI()


def opening_effectiveness_evaluator(example: Example) -> dict:
    """Evaluate the article's opening effectiveness"""
    evaluation_prompt = """You are an expert editor evaluating an article about {topic}.
    Score the article's opening effectiveness (0-5):
    - Does it explain why the article is important to read?
    - Does it establish author credibility/expertise?
    - Does it hook the reader and provide clear context?
    
    Article to evaluate:
    {article}
    
    Provide scores and brief justification in this format:
    opening_score: X
    justification: Your brief explanation here
    improvement_suggestions: List specific improvements needed for the opening"""

    topic = example.inputs.get("topic", "technology")
    article = example.inputs.get("article", "")

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": evaluation_prompt.format(topic=topic, article=article),
            },
        ],
        temperature=0,
    )

    eval_text = response.choices[0].message.content

    # Parse response
    lines = eval_text.split("\n")
    score = 0
    justification = ""
    improvements = ""

    for line in lines:
        if "opening_score:" in line:
            score = float(line.split(":")[1].strip())
        elif "justification:" in line:
            justification = line.split(":", 1)[1].strip()
        elif "improvement_suggestions:" in line:
            improvements = line.split(":", 1)[1].strip()

    return {
        "score": score / 5,  # Normalize to 0-1 range
        "comment": justification,
        "evaluator_info": {
            "opening_score": score,
            "improvement_suggestions": improvements,
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
    
    Article to evaluate:
    {article}
    
    Provide scores and brief justification in this format:
    writing_score: X
    justification: Your brief explanation here
    improvement_suggestions: List specific writing improvements needed"""

    topic = example.inputs.get("topic", "technology")
    article = example.inputs.get("article", "")

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": evaluation_prompt.format(topic=topic, article=article),
            },
        ],
        temperature=0,
    )

    eval_text = response.choices[0].message.content

    # Parse response
    lines = eval_text.split("\n")
    score = 0
    justification = ""
    improvements = ""

    for line in lines:
        if "writing_score:" in line:
            score = float(line.split(":")[1].strip())
        elif "justification:" in line:
            justification = line.split(":", 1)[1].strip()
        elif "improvement_suggestions:" in line:
            improvements = line.split(":", 1)[1].strip()

    return {
        "score": score / 5,  # Normalize to 0-1 range
        "comment": justification,
        "evaluator_info": {
            "writing_score": score,
            "improvement_suggestions": improvements,
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
    
    Article to evaluate:
    {article}
    
    Provide scores and brief justification in this format:
    technical_score: X
    justification: Your brief explanation here
    improvement_suggestions: List specific technical presentation improvements needed"""

    topic = example.inputs.get("topic", "technology")
    article = example.inputs.get("article", "")

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": evaluation_prompt.format(topic=topic, article=article),
            },
        ],
        temperature=0,
    )

    eval_text = response.choices[0].message.content

    # Parse response
    lines = eval_text.split("\n")
    score = 0
    justification = ""
    improvements = ""

    for line in lines:
        if "technical_score:" in line:
            score = float(line.split(":")[1].strip())
        elif "justification:" in line:
            justification = line.split(":", 1)[1].strip()
        elif "improvement_suggestions:" in line:
            improvements = line.split(":", 1)[1].strip()

    return {
        "score": score / 5,  # Normalize to 0-1 range
        "comment": justification,
        "evaluator_info": {
            "technical_score": score,
            "improvement_suggestions": improvements,
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
    
    Article to evaluate:
    {article}
    
    Provide scores and brief justification in this format:
    references_score: X
    justification: Your brief explanation here
    improvement_suggestions: List specific improvements needed for references and support"""

    topic = example.inputs.get("topic", "technology")
    article = example.inputs.get("article", "")

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": evaluation_prompt.format(topic=topic, article=article),
            },
        ],
        temperature=0,
    )

    eval_text = response.choices[0].message.content

    # Parse response
    lines = eval_text.split("\n")
    score = 0
    justification = ""
    improvements = ""

    for line in lines:
        if "references_score:" in line:
            score = float(line.split(":")[1].strip())
        elif "justification:" in line:
            justification = line.split(":", 1)[1].strip()
        elif "improvement_suggestions:" in line:
            improvements = line.split(":", 1)[1].strip()

    return {
        "score": score / 5,  # Normalize to 0-1 range
        "comment": justification,
        "evaluator_info": {
            "references_score": score,
            "improvement_suggestions": improvements,
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
