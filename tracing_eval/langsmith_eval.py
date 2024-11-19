import datetime
import uuid
from langsmith import Client
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run
from tracing_example import client as openai_client
from generate_some_traces import get_article_summary
from example_article import invest_ottawa_article
from prompts import (
    system_prompt_article_summary,
    system_prompt_article_summary_pirate,
    system_prompt_article_summary_second_grade,
)

# Initialize LangSmith client
langsmith_client = Client()


def generate_traces():
    """Generate traces only if needed"""
    # Check existing runs first
    five_days_ago = datetime.datetime.now() - datetime.timedelta(days=5)
    existing_runs = list(
        langsmith_client.list_runs(
            start_time=five_days_ago,
            project_name="workshops",
            error=False,
            execution_order=1,
        )
    )

    print(f"\nFound {len(existing_runs)} existing runs")

    if len(existing_runs) >= 10:
        print("Already have enough runs, skipping trace generation")
        return existing_runs

    # Calculate how many more runs we need
    runs_needed = 12 - len(existing_runs)
    print(f"Generating {runs_needed} more traces...")

    # Generate only the needed number of runs
    prompts = [
        system_prompt_article_summary,
        system_prompt_article_summary_pirate,
        system_prompt_article_summary_second_grade,
    ]

    # Cycle through prompts until we have enough runs
    for prompt in (prompts * ((runs_needed + 2) // 3))[:runs_needed]:
        get_article_summary(invest_ottawa_article, prompt)

    # Get updated list of runs including the new ones
    return list(
        langsmith_client.list_runs(
            start_time=five_days_ago,
            project_name="workshops",
            error=False,
            execution_order=1,
        )
    )


def create_dataset_from_recent_traces(runs_list):
    """Create a dataset from traces"""
    # Create unique dataset name with UUID and timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    dataset_name = f"Article_Summary_Eval_{timestamp}_{unique_id}"

    # Create dataset
    dataset = langsmith_client.create_dataset(
        dataset_name,
        description=f"Article summaries evaluation dataset (created {timestamp})",
    )

    if not runs_list:
        raise ValueError("No runs provided. Make sure traces were generated.")

    # Store the generated summary in the outputs
    inputs = [{"article": run.inputs.get("article_text", "")} for run in runs_list]

    outputs = []
    for run in runs_list:
        output_text = run.outputs.get("text", "")
        if not output_text:
            # Try alternative output paths
            output_text = (
                run.outputs.get("output", "")
                or run.outputs.get("content", "")
                or run.outputs.get("response", "")
            )
        outputs.append({"summary": output_text})

    # Use our runs to create examples in the eval dataset
    print(f"\nCreating {len(inputs)} examples in dataset")
    langsmith_client.create_examples(
        inputs=inputs, outputs=outputs, dataset_id=dataset.id
    )

    # Verify dataset creation
    examples = list(langsmith_client.list_examples(dataset_id=dataset.id))
    print(f"\nCreated dataset with {len(examples)} examples")

    return dataset


def professional_tone_evaluator(example: Example) -> dict:
    """Evaluate if the summary has a professional tone"""
    evaluation_prompt = """You are a professional editor evaluating article summaries.
    Evaluate if the following summary maintains a professional tone and avoids overly excited or informal language.
    Score 1 if the tone is professional, 0 if it's too informal or excited.
    
    Summary to evaluate:
    {summary}
    
    Respond with only a number: 1 for professional, 0 for unprofessional."""

    # Get the summary from the example outputs (not run outputs)
    summary = example.outputs.get("summary", "")
    if not summary:
        print("Warning: No summary found in example outputs")
        return {
            "score": 0,
            "key": "professional_tone",
            "comment": "No summary found to evaluate",
        }

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": evaluation_prompt.format(summary=summary)},
            {"role": "user", "content": summary},
        ],
        temperature=0,
    )

    score = int(response.choices[0].message.content.strip())
    return {
        "score": score,
        "key": "professional_tone",
        "comment": "1 indicates professional tone, 0 indicates informal/excited tone",
    }


def run_evaluation():
    """Run the entire evaluation process"""
    # Generate traces if needed and get list of runs
    print("Checking and generating traces if needed...")
    runs_list = generate_traces()

    # Create dataset using the runs we already have
    print("\nCreating dataset from traces...")
    dataset = create_dataset_from_recent_traces(runs_list)

    # Run evaluation
    print("\nRunning evaluation...")
    results = evaluate(
        lambda x: x,
        dataset.name,
        evaluators=[professional_tone_evaluator],
        experiment_prefix="Professional_Tone_Analysis",
    )

    print("\nEvaluation complete! Check results in LangSmith UI")
    return results


if __name__ == "__main__":
    run_evaluation()
