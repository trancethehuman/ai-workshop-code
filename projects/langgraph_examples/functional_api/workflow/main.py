from asyncio import Future
import os
import uuid
from dotenv import load_dotenv

from google import genai
from google.genai import types

from langgraph.func import entrypoint, task
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

load_dotenv()

# Create a client for the Gemini Developer API.
# We set the API version to 'v1alpha' as per the instructions.
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"], http_options={"api_version": "v1alpha"}
)


# ------------------------------------------------------------------------------
# Helper Function to Generate Content via Gemini
# ------------------------------------------------------------------------------
def gemini_generate(prompt: str) -> str:
    """
    Generates content using the Gemini model.
    The provided prompt is combined with a system instruction.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite-preview-02-05",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You're an expert at writing jokes. Your jokes are always one-liner and 4 words. "
                "You never start with the same premise for jokes. "
                "You must respond with only the joke."
            ),
            temperature=1,
            top_p=0.95,
            top_k=40,
            max_output_tokens=8192,
        ),
    )
    if response.text is None:
        raise ValueError("Gemini API returned None response")
    return response.text


# ------------------------------------------------------------------------------
# Define Tasks because it's LangGraph type shihhhh
# ------------------------------------------------------------------------------


@task
def generate_oneliner(word: str) -> dict:
    """
    Generates a creative one-liner using the provided word.
    Returns a dictionary with the generated draft.
    """
    prompt = f"Write a creative one-liner using the word '{word}'."
    draft = gemini_generate(prompt)
    return {"draft": draft}


@task
def revise_oneliner(original: str, feedback: str) -> dict:
    """
    Revises the one-liner based on human feedback.
    Returns a dictionary with the revised draft.
    """
    prompt = (
        f"Revise the following one-liner based on this feedback. Don't write a similar joke.\n\n"
        f"Feedback: {feedback}\n"
        f"Original: {original}\n\n"
        f"Revised one-liner:"
    )
    revised = gemini_generate(prompt)
    return {"revised": revised}


# ------------------------------------------------------------------------------
# Define the Main Workflow as an Entrypoint
# ------------------------------------------------------------------------------


@entrypoint(checkpointer=MemorySaver())
def workflow(
    user_input: str, previous: dict | None = None
) -> entrypoint.final[dict, dict]:
    """
    Workflow steps:
      1. Generate a one-liner based on the input word.
      2. Use the LangGraph interrupt mechanism to request human review.
      3. If approved (input equals 'yes'), accept the generated draft.
         Otherwise, revise the draft based on the provided feedback.
      4. Return the final draft.

    Using the same thread ID across invocations enables state persistence ("time travel").
    """
    # (Optionally, you could inspect the previous state here if needed.)
    gen_result = generate_oneliner(user_input).result()
    draft = gen_result["draft"]
    print("\nGenerated Draft:")
    print(draft)

    # --- Step 2: Human-in-the-Loop Approval using interrupt ---
    # This will raise a GraphInterrupt on first execution and then, on resume (via Command),
    # it will return the human-provided value.
    approval = interrupt(
        {
            "generated_draft": draft,
            "action": "Please approve this one-liner by typing 'yes' or provide your feedback for revision.",
        }
    )
    # If no resume value is provided by the client, fall back to manual input.
    if approval is None:
        approval = input(
            "Interrupt Resume - Please type 'yes' to approve or provide feedback: "
        ).strip()

    # --- Step 3: Decide Based on Human Input ---
    if approval.lower() == "yes":
        final_draft = draft
        print("Draft approved.")
    else:
        rev_result = revise_oneliner(draft, approval).result()
        final_draft = rev_result["revised"]
        print("Revised Draft:")
        print(final_draft)

    # Return the final draft; additional state (including checkpoint metadata) is managed by LangGraph.
    return entrypoint.final(
        value={"final_draft": final_draft}, save={"final_draft": final_draft}
    )


# ------------------------------------------------------------------------------
# Main Execution Block with Looping (Using the Same Thread ID for Persistent State)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Use a single thread ID for all iterations so that the entire checkpoint history is maintained.
    thread_id = str(uuid.uuid4())

    print("Starting the workflow loop. Type 'quit' at any prompt to exit.\n")
    while True:
        user_word = input("Enter a word: ").strip()
        if user_word.lower() == "quit":
            break

        # Invoke the workflow with the given word using the same thread ID.
        result = workflow.invoke(user_word, {"configurable": {"thread_id": thread_id}})
        # If the workflow was interrupted and did not complete, result will be None.
        if result is None:
            # Retrieve the saved state.
            last_state = workflow.get_state({"configurable": {"thread_id": thread_id}})
            # Try to extract the interrupt payload via the state's helper (if available).
            interrupt_state = getattr(last_state, "get_interrupt", lambda: None)()
            if interrupt_state is not None:
                resume_value = input(f"{interrupt_state['action']}\n").strip()
            else:
                resume_value = input(
                    "Please approve this one-liner by typing 'yes' or provide feedback: "
                ).strip()
            result = workflow.invoke(
                Command(resume=resume_value), {"configurable": {"thread_id": thread_id}}
            )
        if result is None:
            result = workflow.get_state({"configurable": {"thread_id": thread_id}})

        # Display the final draft.
        print("\n=== Workflow Result ===")
        print("Final Draft:")
        print(result["final_draft"])

        # Retrieve and display checkpoint (state history) data as generated by LangGraph.
        state_history = list(
            workflow.get_state_history({"configurable": {"thread_id": thread_id}})
        )
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
                        parent_checkpoint_id = parent_config.get(
                            "configurable", {}
                        ).get("checkpoint_id", "N/A")
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

        print("----- End of this iteration -----\n")
