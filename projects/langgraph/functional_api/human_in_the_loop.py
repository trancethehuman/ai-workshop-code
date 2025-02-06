from typing import Dict
from langgraph.types import Command
from utils import display_workflow_state


def get_user_feedback() -> str:
    """Get feedback from the user for essay approval or revision."""
    return input(
        "\nEnter 'yes' to approve the essay, or provide your feedback for revision: "
    ).strip()


def handle_interrupt(payload: Dict) -> Command:
    """
    Handle the workflow interruption by displaying the current state
    and getting user feedback.

    Args:
        payload: Dictionary containing the current workflow state

    Returns:
        Command object with the user's response
    """
    display_workflow_state(payload)
    user_response = get_user_feedback()
    return Command(resume=user_response)
