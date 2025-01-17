import os
import glob
from datetime import datetime
import uuid
from tabulate import tabulate
from langsmith import Client
from langsmith.evaluation import evaluate
from dotenv import load_dotenv

load_dotenv()

# Initialize LangSmith client
langsmith_client = Client()


def read_articles_from_directory():
    """Read all articles from the generated_articles directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    articles_dir = os.path.join(current_dir, "generated_articles")

    articles = []
    for filepath in glob.glob(os.path.join(articles_dir, "*.txt")):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            filename = os.path.basename(filepath)
            # Extract topic from filename (everything before first underscore)
            topic = " ".join(filename.split("_")[0].split("-")).title()
            articles.append({"topic": topic, "content": content, "filename": filename})

    return articles


def create_evaluation_dataset(articles):
    """Create a dataset from the articles for evaluation"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    dataset_name = f"Technical_Articles_Eval_{timestamp}_{unique_id}"

    dataset = langsmith_client.create_dataset(
        dataset_name,
        description=f"Technical articles evaluation dataset (created {timestamp})",
    )

    # Prepare inputs and outputs separately as required by the API
    inputs = []
    outputs = []

    for article in articles:
        inputs.append({"article": article["content"], "topic": article["topic"]})
        outputs.append({"article": article["content"], "topic": article["topic"]})

    # Create examples using the correct API format
    langsmith_client.create_examples(
        dataset_id=dataset.id, inputs=inputs, outputs=outputs
    )

    return dataset


def wrap_text(text: str, width: int = 60) -> str:
    """Wrap text to specified width while preserving line breaks"""
    lines = []
    for line in text.split("\n"):
        while len(line) > width:
            # Find the last space within the width limit
            split_point = line[:width].rfind(" ")
            if split_point == -1:  # No space found, force split at width
                split_point = width
            lines.append(line[:split_point])
            line = line[split_point:].lstrip()
        lines.append(line)
    return "\n".join(lines)


def format_evaluation_results(results):
    """Format evaluation results into tables"""
    # Prepare data for table
    table_data = []
    headers = ["Article", "Technical", "Readability", "Style & Trust", "Details"]

    # Iterate over the results
    for result in results:
        try:
            # Get the example data (Example object)
            example = result["example"]
            topic = example.inputs.get("topic", "Unknown Topic")

            # Initialize row data
            row_data = [topic]
            scores = {"technical_quality": "", "readability": "", "style_and_trust": ""}
            details = []

            # Process evaluation results
            eval_results = result["evaluation_results"]["results"]
            for eval_result in eval_results:
                scores[eval_result.key] = f"{eval_result.score:.2f}"

                # Get the evaluator's comment and metadata
                comment = (
                    eval_result.comment
                    if eval_result.comment
                    else "No explanation provided"
                )
                evaluator_info = (
                    eval_result.evaluator_info if eval_result.evaluator_info else {}
                )

                if eval_result.key == "style_and_trust":
                    details.append("Style & Trust Evaluation:")
                    details.append(
                        f"Explanation: {comment[:200]}..."
                    )  # Truncate long explanations
                    if "improvement_suggestions" in evaluator_info:
                        improvements = evaluator_info["improvement_suggestions"]
                        details.append(
                            f"Improvements needed: {improvements[:150]}..."
                        )  # Truncate long lists
                    if evaluator_info:
                        details.append("Scores:")  # Shortened header
                        for key, value in evaluator_info.items():
                            if key not in ["improvement_suggestions"]:
                                details.append(f"- {key}: {value}")
                elif eval_result.key == "technical_quality":
                    details.append("\nTechnical Quality:")  # Shortened header
                    details.append(
                        f"Explanation: {comment[:200]}..."
                    )  # Truncate long explanations
                    if evaluator_info:
                        details.append("Scores:")  # Shortened header
                        for key, value in evaluator_info.items():
                            details.append(f"- {key}: {value}")
                elif eval_result.key == "readability":
                    details.append("\nReadability:")  # Shortened header
                    details.append(
                        f"Explanation: {comment[:200]}..."
                    )  # Truncate long explanations
                    if evaluator_info:
                        details.append("Scores:")  # Shortened header
                        for key, value in evaluator_info.items():
                            details.append(f"- {key}: {value}")

            # Format the details with proper wrapping
            formatted_details = wrap_text("\n".join(details))

            row_data.extend(
                [
                    scores.get("technical_quality", ""),
                    scores.get("readability", ""),
                    scores.get("style_and_trust", ""),
                    formatted_details,
                ]
            )
            table_data.append(row_data)

        except Exception as e:
            print(f"Error processing result: {str(e)}")
            continue

    return table_data, headers


def print_evaluation_tables(table_data, headers):
    """Print formatted evaluation tables"""
    # Print results table
    print("\nEvaluation Results:")
    print(
        tabulate(
            table_data,
            headers=headers,
            tablefmt="grid",
            numalign="center",
            stralign="left",
        )
    )

    # Calculate and print average scores
    if table_data:
        # Filter out empty scores and convert to float
        tech_scores = [float(row[1]) for row in table_data if row[1]]
        read_scores = [float(row[2]) for row in table_data if row[2]]
        style_scores = [float(row[3]) for row in table_data if row[3]]

        # Calculate averages only if we have scores
        avg_scores = []
        if tech_scores:
            avg_scores.append(
                ["Technical Quality", f"{sum(tech_scores) / len(tech_scores):.2f}"]
            )
        if read_scores:
            avg_scores.append(
                ["Readability", f"{sum(read_scores) / len(read_scores):.2f}"]
            )
        if style_scores:
            avg_scores.append(
                ["Style & Trust", f"{sum(style_scores) / len(style_scores):.2f}"]
            )

        if avg_scores:
            print("\nAverage Scores:")
            print(
                tabulate(
                    avg_scores,
                    headers=["Metric", "Average Score"],
                    tablefmt="grid",
                    numalign="center",
                )
            )
        else:
            print("\nNo scores available to calculate averages.")


def run_evaluators(dataset_name, evaluators):
    """Run the evaluation process with the given evaluators"""
    return evaluate(
        lambda x: x,
        dataset_name,
        evaluators=evaluators,
        experiment_prefix="Technical_Article_Analysis",
    )
