from litellm import completion
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# The OPENAI_API_KEY will now be automatically loaded from .env
response = completion(
  model="gemini/gemini-pro",
  messages=[{ "role": "user",
             "content": "Hello, how are you?"}]
)

print(response.choices[0].message.content)