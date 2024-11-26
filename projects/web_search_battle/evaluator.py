from langsmith.schemas import Example
import openai
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from langsmith.evaluation import evaluate
from langsmith.wrappers import wrap_openai
from langsmith import traceable

load_dotenv()

# Initialize OpenAI client
openai_client = wrap_openai(openai.Client())


class EvaluationResult(BaseModel):
    score: float
    explanation: str


def search_accuracy_evaluator(
    outputs: dict, reference_outputs: dict, inputs: dict
) -> dict:
    """Evaluate the accuracy of search responses compared to ground truth"""
    system_prompt = """You are an expert evaluator comparing a student's answers to reference ground truth answers.
    
    You must return a JSON object with exactly these fields:
    {
        "score": float,  // 1 or 0
        "explanation": string  // A brief explanation of the score
    }
    
    Score the response based on these criteria:
    - 1.0: Match or equivalent meaning and truthful compared to reference answer
    - 0.0: Incorrect or contradictory
    
    Base your evaluation on accuracy and completeness of information. Do not rely on your own knowledge,
    but really entirely on the reference ground truth answer to grade the student's answer.

    Remember that the ground truth answer is always correct and you cannot dispute this.
    It's normally fine if the student's answer adds extra details as long as the main detail is correct.
    For example, if the student added location, dates to the answer but the reference answer doesn't have those, that's
    fine.
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Get the actual output and reference from the dictionaries
            prediction = outputs.get("output", "")
            reference = reference_outputs.get("reference", "")
            original_question = inputs.get(
                "input", ""
            )  # Get the original question from inputs

            @traceable(
                name="gpt-4o",
                run_type="llm",
                metadata={"ls_provider": "openai", "ls_model_name": "gpt-4o"},
            )
            def get_llm_response(
                system_prompt: str, reference: str, prediction: str, question: str
            ) -> EvaluationResult:
                completion = openai_client.beta.chat.completions.parse(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": f"""
                            Original Question: {question}
                            Reference Answer: {reference}
                            Student Answer: {prediction}
                            """,
                        },
                    ],
                    response_format=EvaluationResult,
                )

                return completion.choices[0].message.parsed

            result = get_llm_response(
                system_prompt, reference, prediction, original_question
            )

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
