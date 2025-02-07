def display_workflow_result(result):
    """Display the final draft from the workflow result."""
    print("\n=== Workflow Result ===")
    print("Final Draft:")
    print(result["final_draft"])


def display_state_history(state_history):
    """Display detailed information about the workflow state history."""
    print("\nAggregated snapshots from State History:")
    for idx, snapshot in enumerate(state_history, 1):
        print(f"\nSnapshot {idx}:")
        created_at = getattr(snapshot, "created_at", "Unknown")
        print(f"  Created at: {created_at}")

        checkpoint_id = "N/A"
        if hasattr(snapshot, "config"):
            try:
                config = snapshot.config
                if isinstance(config, dict):
                    checkpoint_id = config.get("configurable", {}).get(
                        "checkpoint_id", "N/A"
                    )
                else:
                    checkpoint_id = "N/A"
            except Exception:
                checkpoint_id = "N/A"
        print(f"  Checkpoint ID: {checkpoint_id}")

        parent_checkpoint_id = "N/A"
        if hasattr(snapshot, "parent_config") and snapshot.parent_config:
            try:
                parent_config = snapshot.parent_config
                if isinstance(parent_config, dict):
                    parent_checkpoint_id = parent_config.get("configurable", {}).get(
                        "checkpoint_id", "N/A"
                    )
                else:
                    parent_checkpoint_id = "N/A"
            except Exception:
                parent_checkpoint_id = "N/A"
        print(f"  Parent Checkpoint ID: {parent_checkpoint_id}")

        source = "Unknown"
        if hasattr(snapshot, "metadata"):
            try:
                metadata = snapshot.metadata
                if isinstance(metadata, dict):
                    source = metadata.get("source", "Unknown")
                else:
                    source = "Unknown"
            except Exception:
                source = "Unknown"
        print(f"  Source: {source}")

        if hasattr(snapshot, "tasks") and snapshot.tasks:
            for task in snapshot.tasks:
                interrupts = []
                try:
                    interrupts = task.interrupts
                except Exception:
                    interrupts = []
                if interrupts:
                    print("  Task Interrupts:")
                    for intr in interrupts:
                        try:
                            intr_value = intr.value
                        except Exception:
                            intr_value = "N/A"
                        try:
                            intr_when = intr.when
                        except Exception:
                            intr_when = "N/A"
                        try:
                            intr_ns = intr.ns
                        except Exception:
                            intr_ns = "N/A"
                        try:
                            intr_resumable = intr.resumable
                        except Exception:
                            intr_resumable = "N/A"
                        print(f"    - Value: {intr_value}")
                        print(f"      When: {intr_when}")
                        print(f"      NS: {intr_ns}")
                        print(f"      Resumable: {intr_resumable}")
                else:
                    print("  No Interrupt in this task.")
        else:
            print("  No tasks available.")
