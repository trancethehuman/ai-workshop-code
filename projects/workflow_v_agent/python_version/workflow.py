from google import genai
from dotenv import load_dotenv
import os
from generator import generate_haiku
from evaluator import evaluate_haiku
import time
from console_display import (
    print_header,
    print_step,
    print_haiku,
    print_evaluation,
    get_user_input,
    wait_for_enter,
    print_success,
    print_error,
    print_welcome,
)

load_dotenv()

# Model name
model_name = "gemini-2.0-flash"

# Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def haiku_workflow():
    print_header("Cat Haiku Generator")
    prompt = get_user_input("Please provide a theme or inspiration")
    wait_for_enter("Press Enter to start generating")

    feedback = None
    iteration = 1
    max_iterations = 7

    while iteration <= max_iterations:
        print_header(f"Iteration {iteration}/{max_iterations}")

        print_step("Generating haiku...")
        time.sleep(0.5)
        haiku = generate_haiku(client, model_name, prompt, feedback)
        print_haiku(haiku)

        wait_for_enter("Press Enter to evaluate")

        print_step("Evaluating haiku...")
        time.sleep(0.5)
        evaluation = evaluate_haiku(client, model_name, haiku)
        print_evaluation(evaluation)

        if evaluation.strip() == "good_enough":
            print_success("🎉 Success! Created a perfect cat haiku! 🐱")
            return haiku

        feedback = evaluation
        iteration += 1

        if iteration <= max_iterations:
            wait_for_enter("Press Enter for next version")

    print_error("⚠️  Reached maximum iterations. Here's the last attempt:")
    return haiku


if __name__ == "__main__":
    try:
        print_welcome()
        final_haiku = haiku_workflow()
        print_header("Final Haiku")
        print_haiku(final_haiku)
        wait_for_enter("Press Enter to exit")
    except KeyboardInterrupt:
        print_error("Program terminated by user.")
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
