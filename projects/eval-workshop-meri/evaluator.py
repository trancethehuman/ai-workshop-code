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


def technical_accuracy_evaluator(example: Example) -> dict:
    """Evaluate technical accuracy and depth of the article"""
    evaluation_prompt = """You are a technical expert evaluating an article about {topic}.
    Score the article on technical accuracy and depth using these criteria:
    1. Accuracy of technical information (0-5)
    2. Depth of coverage (0-5)
    3. Use of relevant examples and explanations (0-5)
    
    Article to evaluate:
    {article}
    
    Provide scores and brief justification in this format:
    accuracy_score: X
    depth_score: X
    examples_score: X
    justification: Your brief explanation here"""

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

    # Parse scores from response
    lines = eval_text.split("\n")
    scores = {}
    justification = ""

    for line in lines:
        if "score:" in line:
            key, value = line.split(":")
            scores[key.strip()] = float(value.strip())
        elif "justification:" in line:
            justification = line.split(":", 1)[1].strip()

    # Calculate average score
    avg_score = sum(scores.values()) / len(scores)

    return {
        "score": avg_score / 5,  # Normalize to 0-1 range
        "comment": justification,  # Use comment for LangSmith compatibility
        "evaluator_info": {  # Use evaluator_info for additional metadata
            "accuracy_score": scores.get("accuracy_score", 0),
            "depth_score": scores.get("depth_score", 0),
            "examples_score": scores.get("examples_score", 0),
        },
        "key": "technical_quality",
    }


def readability_evaluator(example: Example) -> dict:
    """Evaluate readability and clarity of the article"""
    evaluation_prompt = """Evaluate the readability and clarity of this technical article about {topic}.
    Score these aspects (0-5):
    1. Clear structure and organization
    2. Appropriate language level for technical audience
    3. Effective use of transitions and flow
    
    Article to evaluate:
    {article}
    
    Provide scores and brief justification in this format:
    structure_score: X
    language_score: X
    flow_score: X
    justification: Your brief explanation here"""

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

    # Parse scores from response
    lines = eval_text.split("\n")
    scores = {}
    justification = ""

    for line in lines:
        if "score:" in line:
            key, value = line.split(":")
            scores[key.strip()] = float(value.strip())
        elif "justification:" in line:
            justification = line.split(":", 1)[1].strip()

    # Calculate average score
    avg_score = sum(scores.values()) / len(scores)

    return {
        "score": avg_score / 5,  # Normalize to 0-1 range
        "comment": justification,  # Use comment for LangSmith compatibility
        "evaluator_info": {  # Use evaluator_info for additional metadata
            "structure_score": scores.get("structure_score", 0),
            "language_score": scores.get("language_score", 0),
            "flow_score": scores.get("flow_score", 0),
        },
        "key": "readability",
    }


def style_and_trust_evaluator(example: Example) -> dict:
    """Evaluate the article's style, trust factors, and writing quality"""
    evaluation_prompt = """You are an expert editor evaluating an article about {topic}.
    Score the article on these specific criteria (0-5 for each):

    1. Opening Effectiveness:
       - Does it explain why the article is important to read?
       - Does it establish author credibility/expertise?

    2. Writing Quality:
       - Is it concise without filler words?
       - Are paragraphs and sentences appropriately sized?
       - Avoids overused LLM phrases (like "let's dive in", "let's explore", "dwelve into")?

    3. Technical Presentation:
       - Is code (if present) simple to understand?
       - Are technical concepts clearly explained?

    4. References and Support:
       - Are references or sources included?
       - Are claims properly supported?

    Article to evaluate:
    {article}

    Provide scores and brief justification in this format:
    opening_score: X
    writing_quality_score: X
    technical_presentation_score: X
    references_score: X
    justification: Your brief explanation here
    improvement_suggestions: List specific improvements needed"""

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

    # Parse scores from response
    lines = eval_text.split("\n")
    scores = {}
    justification = ""
    improvements = ""

    for line in lines:
        if "score:" in line:
            key, value = line.split(":")
            scores[key.strip()] = float(value.strip())
        elif "justification:" in line:
            justification = line.split(":", 1)[1].strip()
        elif "improvement_suggestions:" in line:
            improvements = line.split(":", 1)[1].strip()

    # Calculate average score
    avg_score = sum(scores.values()) / len(scores)

    return {
        "score": avg_score / 5,  # Normalize to 0-1 range
        "comment": justification,  # Use comment for LangSmith compatibility
        "evaluator_info": {  # Use evaluator_info for additional metadata
            "opening_score": scores.get("opening_score", 0),
            "writing_quality_score": scores.get("writing_quality_score", 0),
            "technical_presentation_score": scores.get(
                "technical_presentation_score", 0
            ),
            "references_score": scores.get("references_score", 0),
            "improvement_suggestions": improvements,
        },
        "key": "style_and_trust",
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
        # technical_accuracy_evaluator,
        # readability_evaluator,
        style_and_trust_evaluator,
    ]
    results = run_evaluators(dataset.name, evaluators)

    print("\nEvaluation complete! Results are available in LangSmith UI")

    # Format and print results
    table_data, headers = format_evaluation_results(results)
    print_evaluation_tables(table_data, headers)

    return results


if __name__ == "__main__":
    run_evaluation()
