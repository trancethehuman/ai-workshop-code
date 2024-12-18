from openai import OpenAI
from dotenv import load_dotenv
from langsmith import traceable
import os
from pydantic import BaseModel
from consts import IMG_URLS, OCR_SYSTEM_PROMPT, MODELS

load_dotenv()

client = OpenAI()


class OCRResponse(BaseModel):
    text: str


def get_ocr_openai(image_url: str, model_name: str) -> str:
    @traceable(name=model_name, run_type="llm")
    def _traced_ocr(url: str) -> str:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
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
                            "image_url": {
                                "url": url,
                            },
                        },
                    ],
                },
            ],
            temperature=0,
            max_tokens=4096,
        )

        return response.choices[0].message.content

    return _traced_ocr(image_url)


def test_openai_models():
    # Get the first image URL for testing
    test_image = IMG_URLS[0]
    print(f"Testing with image: {test_image}\n")

    # Filter for OpenAI models
    openai_models = [m for m in MODELS if m["provider"] == "openai"]

    for model in openai_models:
        print(f"\nTesting {model['name']}")
        print("-" * 30)
        try:
            result = get_ocr_openai(test_image, model["name"])
            print(f"Result:\n{result}")
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 30)


if __name__ == "__main__":
    test_openai_models()
