from asyncio import Future
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

from google import genai
from google.genai import types

from langgraph.func import entrypoint, task
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables (e.g., GEMINI_API_KEY)
load_dotenv()

# Create a client for the Gemini Developer API.
# Note: We set the API version to 'v1alpha' per the instructions.
client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"], http_options={"api_version": "v1alpha"}
)


# ------------------------------------------------------------------------------
# Helper function to generate content via the Gemini API.
# ------------------------------------------------------------------------------
def gemini_generate(prompt: str) -> str:
    """
    Generates content using the Gemini model.
    Uses the provided prompt along with a system instruction.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite-preview-02-05",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You're an expert at writing jokes. Your jokes are always one-liner. "
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
# Define Tasks
# ------------------------------------------------------------------------------


@task
def generate_oneliner(word: str) -> dict:
    """
    Task to generate a creative one-liner from the given word using Gemini.
    Returns a Future containing a dictionary with the generated draft and a checkpoint ID.
    """
    prompt = f"Write a creative one-liner using the word '{word}'."
    draft = gemini_generate(prompt)
    cp_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"draft": draft, "checkpoint_id": cp_id, "timestamp": timestamp}


@task
def revise_oneliner(original: str, feedback: str) -> dict:
    """
    Task to revise the one-liner based on the provided feedback using Gemini.
    Returns a dictionary with the revised draft and a new simulated checkpoint ID.
    """
    prompt = (
        f"Revise the following one-liner based on this feedback.\n\n"
        f"Feedback: {feedback}\n"
        f"Original: {original}\n\n"
        f"Revised one-liner:"
    )
    revised = gemini_generate(prompt)
    cp_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"revised": revised, "checkpoint_id": cp_id, "timestamp": timestamp}


# ------------------------------------------------------------------------------
# Define the main workflow as an entrypoint.
# ------------------------------------------------------------------------------
@entrypoint(checkpointer=MemorySaver())
def workflow(
    user_input: str, previous: dict | None = None
) -> entrypoint.final[dict, dict]:
    """
    Workflow:
      1. Generates a draft one-liner from the input word.
      2. Asks for human approval (or feedback) to decide whether to revise.
      3. Returns a dict with the final draft and an aggregated history of all checkpoints.

    The aggregated history is preserved via the same thread ID across iterations.
    """
    # Retrieve aggregated history from previous checkpoint, if available.
    aggregated = previous if previous is not None else {"checkpoints": []}
    current_checkpoints = []  # Checkpoints for the current iteration

    # --- Step 1: Generate the initial one-liner ---
    gen_result = generate_oneliner(user_input).result()
    draft = gen_result["draft"]
    cp_gen = gen_result["checkpoint_id"]
    current_checkpoints.append(
        {
            "task": "generate_oneliner",
            "checkpoint_id": cp_gen,
            "content": draft,
            "timestamp": gen_result["timestamp"],
        }
    )
    print(f"\n[Checkpoint] generate_oneliner -> Checkpoint ID: {cp_gen}")
    print("Generated Draft:")
    print(draft)

    # --- Step 2: Human-in-the-loop approval ---
    print("\nPlease review the generated one-liner above.")
    print("Type 'yes' to approve or type your feedback for revision.")
    approval = input("Your response: ").strip()

    # --- Step 3: Revise if needed ---
    if approval.lower() == "yes":
        final_draft = draft
        print("Draft approved.")
    else:
        task_response = revise_oneliner(draft, approval)
        rev_result = task_response.result()
        final_draft = rev_result["revised"]
        cp_rev = rev_result["checkpoint_id"]
        current_checkpoints.append(
            {
                "task": "revise_oneliner",
                "checkpoint_id": cp_rev,
                "content": final_draft,
                "timestamp": rev_result["timestamp"],
            }
        )
        print(f"\n[Checkpoint] revise_oneliner -> Checkpoint ID: {cp_rev}")
        print("Revised Draft:")
        print(final_draft)

    # --- Final checkpoint for the current iteration ---
    cp_final = str(uuid.uuid4())
    current_checkpoints.append(
        {
            "task": "final_draft",
            "checkpoint_id": cp_final,
            "content": final_draft,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    print(f"\n[Checkpoint] final_draft -> Checkpoint ID: {cp_final}")

    # Merge previous aggregated checkpoints with the current iteration's checkpoints.
    aggregated_checkpoints = aggregated.get("checkpoints", []) + current_checkpoints

    final_output = {"final_draft": final_draft, "checkpoints": aggregated_checkpoints}
    # Save the updated aggregated history in the checkpoint.
    return entrypoint.final(
        value=final_output, save={"checkpoints": aggregated_checkpoints}
    )


# ------------------------------------------------------------------------------
# Main execution block with looping.
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Use a single thread ID for all iterations so that the entire checkpoint history is maintained.
    thread_id = str(uuid.uuid4())

    print("Starting the workflow loop. Type 'quit' at any prompt to exit.\n")
    while True:
        user_word = input("Enter a word: ").strip()
        if user_word.lower() == "quit":
            break
        # Invoke the workflow synchronously with the same thread ID.
        result = workflow.invoke(user_word, {"configurable": {"thread_id": thread_id}})

        # Display the final draft and the aggregated checkpoint history.
        print("\n=== Workflow Result ===")
        print("Final Draft:")
        print(result["final_draft"])
        print("\nAggregated Checkpoints:")
        for idx, cp in enumerate(result["checkpoints"], 1):
            content = cp["content"]
            # Truncate content to first 30 chars and add ellipsis if needed
            truncated_content = content[:30] + ("..." if len(content) > 30 else "")
            print(f"[{idx}]")
            print(f"Time: {cp['timestamp']}")
            print(f"Task: {cp['task']}")
            print(f"ID: {cp['checkpoint_id']}")
            print(f"Content: {truncated_content}\n")

        print("----- End of this iteration -----\n")
