from openai import OpenAI
from dotenv import load_dotenv
from langsmith import traceable
import os
from pydantic import BaseModel
import requests
from consts import OCR_SYSTEM_PROMPT

load_dotenv()

gemini_client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


class OCRResponse(BaseModel):
    text: str


@traceable(name="gemini-2.0-flash-exp", run_type="llm")
def get_ocr_gemini(image_url: str) -> str:
    # Download the image
    response = requests.get(image_url)
    image_data = response.content

    # Convert to base64
    import base64

    base64_image = base64.b64encode(image_data).decode("utf-8")

    messages = [
        {"role": "system", "content": OCR_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Please extract and format all text from this image.",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        },
    ]

    response = gemini_client.chat.completions.create(
        model="gemini-2.0-flash-exp",
        messages=messages,
        temperature=0,
        max_tokens=1000,
    )

    return response.choices[0].message.content
