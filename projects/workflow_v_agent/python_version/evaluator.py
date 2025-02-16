from google import genai
from google.genai import types


def evaluate_haiku(client, model_name, haiku):
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
