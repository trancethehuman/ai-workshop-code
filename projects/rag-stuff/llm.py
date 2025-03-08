from dotenv import load_dotenv
from litellm import completion
from models import QuestionContext

load_dotenv()


def build_prompt(question: str, context: str) -> str:
    """Build a prompt with the question and context"""
    return f"""Based on the following information about Jeff Bezos, please answer this question:
    
Question: {question}

Information:
{context}

Please provide a concise and detailed answer based only on the information provided above.
"""


# Function to query an LLM model with a specific model
def llm_query(user_query: str, model: str) -> str:
    try:
        # Call the LLM through LiteLLM with the specified model
        response = completion(
            model=model,
            messages=[{"role": "user", "content": user_query}],
        )

        # Check response structure and handle potential None values
        if (
            hasattr(response, "choices")
            and response.choices
            and hasattr(response.choices[0], "message")
        ):
            content = response.choices[0].message.content
            return content if content is not None else "No content returned"
        else:
            # Handle the case where the response structure is different
            return str(response)
    except Exception as e:
        error_message = f"Error querying {model}: {e}"
        print(error_message)
        return error_message


def query_model(context: QuestionContext, model: str) -> str:
    """Query a specific model with the prepared context"""
    print(f"\nQuerying {model} with the reranked context...")

    # Generate response using the LLM
    model_output = llm_query(context.prompt, model)

    return model_output
