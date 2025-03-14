import os
from agents import RunContextWrapper, function_tool
from dotenv import load_dotenv
from openai import OpenAI

from models.sales import SalesContext

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")


client = OpenAI(api_key=openai_api_key)


@function_tool
def generate_email(
    wrapper: RunContextWrapper[SalesContext],
) -> str:
    """Generate a personalized outbound sales email based on LinkedIn profile data"""

    if not wrapper.context.get("profile_data"):
        return "Error: No LinkedIn profile data available. Please extract profile data first."

    system_prompt = "You're an expert at writing personalized outbound sales emails. Write a concise, persuasive email that connects with the prospect's background and interests."

    prompt_details = f"""
    RECIPIENT INFORMATION:

    {wrapper.context["name"]}
    
    {wrapper.context["profile_data"]}
    
    
    EMAIL DETAILS:
    - Sender Name: AI Agent Company
    - Sender Company: Company of Agents
    
    Guidelines:
    - Keep the email concise (1 paragraph)
    - Write like Josh Braun (shine a light on a problem that the prospect might not know)
    - No jargons, no hard pitch, just pique interest
    """

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt_details}],
            },
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[],
        temperature=0.7,
        max_output_tokens=2048,
        top_p=1,
        store=True,
    )

    generated_email = response.output_text

    # Update the context with the generated email
    wrapper.context["email_draft"] = generated_email

    return generated_email
