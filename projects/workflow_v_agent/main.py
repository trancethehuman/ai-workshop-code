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

response = client.models.generate_content(
    model=model_name, contents="Why is the sky blue?"
)
print(response.text)
