import uuid
from workflow import workflow
from human_in_the_loop import handle_interrupt
from utils import get_initial_topic


def run_workflow(topic: str) -> None:
    """Run the essay generation workflow with the given topic."""
    # Create a unique thread identifier for checkpointing.
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("\n=== Starting workflow ===")
    while True:
        for output in workflow.stream(topic, config):
            # Simplified interrupt check.
            if "__interrupt__" in output:
                payload = output["__interrupt__"][0].value
                topic = handle_interrupt(payload)
                break
        else:
            print("\n=== Workflow Completed ===")
            print("Final result:", output)
            return


def main():
    """Main entry point for the essay generation application."""
    topic = get_initial_topic()
    run_workflow(topic)


if __name__ == "__main__":
    main()
