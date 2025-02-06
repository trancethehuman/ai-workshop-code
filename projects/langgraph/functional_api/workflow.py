from langgraph.func import entrypoint
from langgraph.types import interrupt
from langgraph.checkpoint.memory import MemorySaver
from .tasks import generate_essay, rework_essay


@entrypoint(checkpointer=MemorySaver())
def workflow(
    initial_topic: str, *, previous: dict = None
) -> entrypoint.final[dict, dict]:
    """
    A workflow that:
      1. Generates an essay about the provided topic using Gemini.
      2. Pauses for human review, allowing free-form feedback.
      3. If the user types 'yes', the essay is approved.
      4. Otherwise, the feedback is passed to the LLM to rework the essay,
         and the revised draft is stored.
      5. Returns the final approved essay along with all past drafts.

    The workflow retrieves (and updates) the topic and past drafts from checkpoint state.
    """
    # Retrieve stored state if available.
    if previous is not None:
        topic = previous.get("topic", initial_topic)
        drafts = previous.get("drafts", [])
        messages = previous.get("messages", [])
        essay = drafts[-1] if drafts else generate_essay(topic).result()
        if not drafts:
            drafts.append(essay)
    else:
        topic = initial_topic
        drafts = []
        messages = []
        essay = generate_essay(topic).result()
        drafts.append(essay)

    # Loop for human review and potential rework.
    while True:
        payload = {
            "topic": topic,
            "current_essay": essay,
            "drafts": drafts,
            "messages": messages,
            "action": (
                "Do you approve the essay? If yes, type 'yes'. Otherwise, "
                "enter your revision feedback."
            ),
        }
        # Pause execution and send payload for human-in-the-loop review.
        user_input = interrupt(payload)

        # If the user replies 'yes' (approval), finish the workflow.
        if isinstance(user_input, str) and user_input.lower() == "yes":
            messages.append("User approved the essay")
            final_result = {
                "final_essay": essay,
                "approved": True,
                "all_drafts": drafts,
                "message_history": messages,
            }
            return entrypoint.final(
                value=final_result,
                save={"topic": topic, "drafts": drafts, "messages": messages},
            )
        else:
            # Otherwise, use the provided feedback for revision.
            feedback = user_input if isinstance(user_input, str) else str(user_input)
            messages.append(f"User feedback: {feedback}")
            essay = rework_essay(essay, topic, feedback).result()
            drafts.append(essay)
