from langgraph.func import task
from .gemini_client import model
from .utils import display_task_header


@task
def generate_essay(topic: str) -> str:
    """
    Generate an essay on the given topic using the Gemini LLM.
    """
    display_task_header("Generating Initial Essay")
    chat_session = model.start_chat()
    response = chat_session.send_message(
        f"Write me an extremely short essay about {topic} in 3 sentences."
    )
    return response.text


@task
def rework_essay(essay: str, topic: str, feedback: str) -> str:
    """
    Rework and improve the provided essay using the Gemini LLM,
    incorporating the provided revision feedback.
    """
    display_task_header("Reworking Essay Based on Feedback")
    chat_session = model.start_chat()
    response = chat_session.send_message(
        f"Revise and improve the following essay about {topic} to make it more engaging while keeping it to 5 sentences.\n"
        f"Here is the feedback: {feedback}\n\n"
        f"{essay}"
    )
    return response.text
