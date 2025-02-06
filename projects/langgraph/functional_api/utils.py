from typing import Dict, List


def display_workflow_state(payload: Dict) -> None:
    """Display the current state of the workflow to the user."""
    print("\n------- Interrupted -------")
    print("Topic:", payload.get("topic"))
    print("Current Essay:")
    print(payload.get("current_essay"))
    print("Past Drafts:")
    for i, draft in enumerate(payload.get("drafts", [])):
        # Display a truncated version of each draft.
        print(f"{i + 1}: {draft[: len(draft) // 10]}...")


def get_initial_topic() -> str:
    """Get the initial topic from the user with default fallback."""
    topic = input("Enter the topic for your essay: ").strip()
    if not topic:
        print("Topic cannot be empty. Using default topic 'technology'")
        topic = "technology"
    return topic


def display_task_header(task_name: str) -> None:
    """Display a header for a task being executed."""
    print(f"\n------- Executing: {task_name} -------")


def format_message_history(messages: List[str]) -> str:
    """Format the message history for display."""
    return "\n".join([f"[{i + 1}] {msg}" for i, msg in enumerate(messages)])
