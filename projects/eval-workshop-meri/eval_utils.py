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
    headers = ["Article", "Opening", "Writing", "Technical", "References", "Details"]

    # Iterate over the results
    for result in results:
        try:
            # Get the example data (Example object)
            example = result["example"]
            topic = example.inputs.get("topic", "Unknown Topic")

            # Initialize row data
            row_data = [topic]
            scores = {
                "opening_effectiveness": "",
                "writing_quality": "",
                "technical_presentation": "",
                "references": "",
            }
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

                if eval_result.key == "opening_effectiveness":
                    details.append("Opening Effectiveness:")
                    details.append(f"Explanation: {comment[:150]}...")
                    if evaluator_info and "improvement_suggestions" in evaluator_info:
                        improvements = evaluator_info["improvement_suggestions"]
                        if improvements:
                            details.append(f"Improvements needed:")
                            # Split improvements if it's a list-like string
                            if "," in improvements or ";" in improvements:
                                for imp in improvements.replace(";", ",").split(","):
                                    imp = imp.strip()
                                    if imp:
                                        details.append(f"- {imp[:100]}")
                            else:
                                details.append(f"- {improvements[:100]}")

                elif eval_result.key == "writing_quality":
                    details.append("\nWriting Quality:")
                    details.append(f"Explanation: {comment[:150]}...")
                    if evaluator_info and "improvement_suggestions" in evaluator_info:
                        improvements = evaluator_info["improvement_suggestions"]
                        if improvements:
                            details.append(f"Improvements needed:")
                            # Split improvements if it's a list-like string
                            if "," in improvements or ";" in improvements:
                                for imp in improvements.replace(";", ",").split(","):
                                    imp = imp.strip()
                                    if imp:
                                        details.append(f"- {imp[:100]}")
                            else:
                                details.append(f"- {improvements[:100]}")

                elif eval_result.key == "technical_presentation":
                    details.append("\nTechnical Presentation:")
                    details.append(f"Explanation: {comment[:150]}...")
                    if evaluator_info and "improvement_suggestions" in evaluator_info:
                        improvements = evaluator_info["improvement_suggestions"]
                        if improvements:
                            details.append(f"Improvements needed:")
                            # Split improvements if it's a list-like string
                            if "," in improvements or ";" in improvements:
                                for imp in improvements.replace(";", ",").split(","):
                                    imp = imp.strip()
                                    if imp:
                                        details.append(f"- {imp[:100]}")
                            else:
                                details.append(f"- {improvements[:100]}")

                elif eval_result.key == "references":
                    details.append("\nReferences & Support:")
                    details.append(f"Explanation: {comment[:150]}...")
                    if evaluator_info and "improvement_suggestions" in evaluator_info:
                        improvements = evaluator_info["improvement_suggestions"]
                        if improvements:
                            details.append(f"Improvements needed:")
                            # Split improvements if it's a list-like string
                            if "," in improvements or ";" in improvements:
                                for imp in improvements.replace(";", ",").split(","):
                                    imp = imp.strip()
                                    if imp:
                                        details.append(f"- {imp[:100]}")
                            else:
                                details.append(f"- {improvements[:100]}")

            # Format the details with proper wrapping
            formatted_details = wrap_text("\n".join(details))

            row_data.extend(
                [
                    scores.get("opening_effectiveness", ""),
                    scores.get("writing_quality", ""),
                    scores.get("technical_presentation", ""),
                    scores.get("references", ""),
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
        opening_scores = [float(row[1]) for row in table_data if row[1]]
        writing_scores = [float(row[2]) for row in table_data if row[2]]
        technical_scores = [float(row[3]) for row in table_data if row[3]]
        reference_scores = [float(row[4]) for row in table_data if row[4]]

        # Calculate averages only if we have scores
        avg_scores = []
        if opening_scores:
            avg_scores.append(
                [
                    "Opening Effectiveness",
                    f"{sum(opening_scores) / len(opening_scores):.2f}",
                ]
            )
        if writing_scores:
            avg_scores.append(
                ["Writing Quality", f"{sum(writing_scores) / len(writing_scores):.2f}"]
            )
        if technical_scores:
            avg_scores.append(
                [
                    "Technical Presentation",
                    f"{sum(technical_scores) / len(technical_scores):.2f}",
                ]
            )
        if reference_scores:
            avg_scores.append(
                [
                    "References & Support",
                    f"{sum(reference_scores) / len(reference_scores):.2f}",
                ]
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
