from openai import OpenAI
from dotenv import load_dotenv
from langsmith import traceable
import os
from pydantic import BaseModel
import requests
from consts import OCR_SYSTEM_PROMPT, MODELS, IMG_URLS

load_dotenv()

gemini_client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


class OCRResponse(BaseModel):
    text: str


def get_ocr_gemini(
    image_url: str, model_name: str, image_name: str, reference: str
) -> str:
    @traceable(name=model_name, run_type="llm", tags=[image_name])
    def _traced_ocr(url: str, reference: str) -> str:
        # Download the image
        response = requests.get(url)
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
            model=model_name,
            messages=messages,
            temperature=0,
            max_tokens=5000,
        )

        return response.choices[0].message.content

    return _traced_ocr(image_url, reference)


def test_gemini_models():
    # Get the first image URL for testing
    test_image = IMG_URLS[0]
    print(f"Testing with image: {test_image['name']}\n")

    # Filter for Gemini models
    gemini_models = [m for m in MODELS if m["provider"] == "google"]

    for model in gemini_models:
        print(f"\nTesting {model['name']}")
        print("-" * 30)
        try:
            result = get_ocr_gemini(
                test_image["url"],
                model["name"],
                test_image["name"],
                test_image["reference"],
            )
            print(f"Result:\n{result}")
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 30)


if __name__ == "__main__":
    test_gemini_models()
