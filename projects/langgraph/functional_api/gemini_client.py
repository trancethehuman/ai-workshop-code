import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure the Gemini API key from your environment.
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Generation configuration for Gemini.
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
    "response_mime_type": "text/plain",
}

# Create the Gemini Generative Model.
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    system_instruction="You're an expert at creative writing",
)
