from langsmith import Client
import datetime
import uuid
from reference import ground_truths

langsmith_client = Client()


def create_evaluation_dataset(PROVIDERS):
    """Create a dataset from the generated responses"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    dataset_name = f"Search_Battle_Eval_{timestamp}_{unique_id}"

    expected_runs = len(PROVIDERS) * len(ground_truths)
    print(
        f"\nExpecting {expected_runs} runs ({len(PROVIDERS)} providers × {len(ground_truths)} queries)"
    )

    # Get existing runs with the search_battle tag
    existing_runs = list(
        langsmith_client.list_runs(
            start_time=datetime.datetime.now() - datetime.timedelta(days=1),
            filter='has(tags, "search_battle")',
            project_name="workshops",
            execution_order=1,
            error=False,
            limit=expected_runs,
        )
    )

    print(f"\nFound {len(existing_runs)} existing runs with search_battle tag")

    if len(existing_runs) < expected_runs:
        print(
            f"⚠️  Warning: Found fewer runs than expected ({len(existing_runs)} < {expected_runs})"
        )
        print("Some providers might have failed or not all queries were processed")

    dataset = langsmith_client.create_dataset(
        dataset_name,
        description=f"Search provider evaluation dataset (created {timestamp})",
    )

    # Map runs to their corresponding ground truth
    run_map = {}
    for run in existing_runs:
        query = run.inputs.get("query", "")
        for truth in ground_truths:
            if truth["input"] == query:
                provider_output = run.outputs.get("output", "")
                print(f"\nDebug - Processing run for {run.name}")
                print(f"Debug - Provider output found: {provider_output}")

                run_map[run.id] = {
                    "query": query,  # Original query
                    "reference_output": truth["output"],  # Ground truth answer
                    "provider": run.name,
                    "provider_output": provider_output,  # Provider's response
                    "sources": run.outputs.get("sources", []),
                    "grounded": run.outputs.get("grounded", False),
                }

    # Create examples from the mapped runs, setting split based on provider
    inputs = []
    outputs = []
    splits = []

    # Track coverage
    provider_coverage = {provider: 0 for provider in PROVIDERS.keys()}
    query_coverage = {truth["input"]: 0 for truth in ground_truths}

    for data in run_map.values():
        # Input contains only the query
        inputs.append(
            {
                "input": data["query"],
                "output": data["provider_output"],
            }
        )
        # Output contains both the provider's output and the reference answer
        outputs.append(
            {
                "output": data["provider_output"],
                "reference": data["reference_output"],
                "input": data["query"],
            }
        )
        splits.append(data["provider"])

        # Track coverage
        provider_coverage[data["provider"]] = (
            provider_coverage.get(data["provider"], 0) + 1
        )
        query_coverage[data["query"]] = query_coverage.get(data["query"], 0) + 1

    langsmith_client.create_examples(
        inputs=inputs,
        outputs=outputs,
        dataset_id=dataset.id,
        splits=splits,
    )

    examples = list(langsmith_client.list_examples(dataset_id=dataset.id))
    print(f"\nCreated dataset with {len(examples)} examples")
    print("Splits created:", set(splits))

    # Print coverage report
    print("\nProvider Coverage:")
    for provider, count in provider_coverage.items():
        expected = len(ground_truths)
        print(f"{provider}: {count}/{expected} queries processed")

    print("\nQuery Coverage:")
    for query, count in query_coverage.items():
        expected = len(PROVIDERS)
        print(f"'{query}': {count}/{expected} providers responded")

    return dataset
