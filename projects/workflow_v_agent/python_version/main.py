from google import (
    genai,
)  # it's confusing but use this SDK instead of Gemini's SDK (per Google)
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

# Model name
model_name = "gemini-2.0-flash"

# Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_haiku(prompt, feedback=None):
    if feedback:
        content = f"""Prompt: {prompt}
Previous feedback to address: {feedback}

Write a haiku that MUST:
1. Be exactly three lines
2. Follow 5-7-5 syllable pattern strictly
3. Include the word "cat" explicitly
4. Be about cats (their behavior, nature, or life)
5. Use vivid imagery

Write your haiku:"""
    else:
        content = f"""Prompt: {prompt}

Write a haiku that MUST:
1. Be exactly three lines
2. Follow 5-7-5 syllable pattern strictly
3. Include the word "cat" explicitly
4. Be about cats (their behavior, nature, or life)
5. Use vivid imagery

Write your haiku:"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=content,
            config=types.GenerateContentConfig(
                temperature=0.7,  # Creative but not too random
                top_p=0.95,
                top_k=20,
                candidate_count=1,
                max_output_tokens=100,
            ),
        )
        if response and response.text:
            return response.text.strip()
        return "Error: No response generated"
    except Exception as e:
        return f"Error generating haiku: {str(e)}"


def evaluate_haiku(haiku):
    content = f"""Strictly evaluate this haiku. ALL criteria must be met for a "good_enough" rating:

    1. MUST contain the word "cat" explicitly (not kitten, feline, etc.)
    2. MUST be exactly three lines
    3. MUST follow 5-7-5 syllable pattern EXACTLY (count each line)
    4. MUST be primarily about cats (their behavior, nature, or life)
    5. MUST use vivid imagery and be creative

    Process:
    1. First, count syllables for each line (must be exactly 5-7-5)
    2. Check if the word "cat" is present
    3. Verify it's about cats specifically
    4. Check for vivid imagery

    Haiku to evaluate:
    {haiku}

    Return EXACTLY "good_enough" ONLY if ALL criteria are met perfectly.
    Otherwise, return ONE SENTENCE about the most critical issue to fix."""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=content,
            config=types.GenerateContentConfig(
                temperature=0.2,  # More deterministic for evaluation
                top_p=0.95,
                top_k=20,
                candidate_count=1,
                max_output_tokens=100,
            ),
        )
        if response and response.text:
            return response.text.strip()
        return "Error: No response generated"
    except Exception as e:
        return f"Error evaluating haiku: {str(e)}"


def haiku_workflow():
    print("\n=== Starting Haiku Generation Workflow ===")
    prompt = input("\nPlease provide a theme or inspiration for the haiku: ")
    input("\nPress Enter to start generating the first haiku...")

    feedback = None
    iteration = 1
    max_iterations = 5

    while iteration <= max_iterations:
        print(f"\n=== Iteration {iteration} ===")
        print("\nGenerating haiku...")
        haiku = generate_haiku(prompt, feedback)
        print(f"\nGenerated Haiku:\n{haiku}")
        input("\nPress Enter to evaluate this haiku...")

        print("\nEvaluating haiku...")
        evaluation = evaluate_haiku(haiku)
        print(f"\nEvaluation Result:\n{evaluation}")

        if evaluation.strip() == "good_enough":
            print("\n🎉 Success! Created a perfect cat haiku!")
            return haiku

        feedback = evaluation
        iteration += 1

        if iteration <= max_iterations:
            input("\nPress Enter to generate the next version...")

    print("\n⚠️ Reached maximum iterations. Here's the last attempt:")
    return haiku


if __name__ == "__main__":
    print("\n🐱 Welcome to the Cat Haiku Generator! 🐱")
    final_haiku = haiku_workflow()
    print("\n=== Final Haiku ===")
    print(final_haiku)
    input("\nPress Enter to exit...")
