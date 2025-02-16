from google.genai import types


def generate_haiku(client, model_name, prompt, feedback=None):
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
