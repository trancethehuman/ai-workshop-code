from langsmith.schemas import Example
import openai
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from langsmith.evaluation import evaluate
from langsmith.wrappers import wrap_openai

load_dotenv()

# Initialize OpenAI client
openai_client = wrap_openai(openai.Client())


class EvaluationResult(BaseModel):
    score: float
    explanation: str


def search_accuracy_evaluator(outputs: dict, reference_outputs: dict) -> dict:
    """Evaluate the accuracy of search responses compared to ground truth"""
    system_prompt = """You are an expert evaluator comparing search results to reference answers.
    
    You must return a JSON object with exactly these fields:
    {
        "score": float,  // A number between 0 and 1
        "explanation": string  // A brief explanation of the score
    }
    
    Score the response based on these criteria:
    - 1.0: Match or equivalent meaning
    - 0.0: Incorrect or contradictory
    
    Base your evaluation on accuracy and completeness of information.
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Get the actual output and reference from the dictionaries
            prediction = outputs.get("output", "")
            reference = reference_outputs.get("reference", "")

            completion = openai_client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"""
                        Reference Answer: {reference}
                        Search Response: {prediction}
                        """,
                    },
                ],
                response_format=EvaluationResult,
            )

            result = completion.choices[0].message.parsed

            return {
                "score": result.score,
                "key": "search_accuracy",
                "comment": result.explanation,
            }
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                print(f"Final evaluation error after {max_retries} attempts: {str(e)}")
                return {
                    "score": 0,
                    "key": "search_accuracy",
                    "comment": f"Evaluation failed after {max_retries} attempts: {str(e)}",
                }
            else:
                print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
