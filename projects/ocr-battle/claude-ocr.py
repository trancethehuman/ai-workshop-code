import anthropic
from dotenv import load_dotenv
from langsmith import traceable
import os
from pydantic import BaseModel
import requests
import base64
from consts import IMG_URLS, OCR_SYSTEM_PROMPT, MODELS

load_dotenv()

client = anthropic.Anthropic()


class OCRResponse(BaseModel):
    text: str


def get_ocr_claude(
    image_url: str, model_name: str, image_name: str, reference: str
) -> str:
    @traceable(name=model_name, run_type="llm", tags=[image_name])
    def _traced_ocr(url: str, reference: str) -> str:
        # Download the image
        response = requests.get(url)
        image_data = base64.b64encode(response.content).decode("utf-8")

        message = client.messages.create(
            model=model_name,
            max_tokens=4096,
            system=OCR_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Please extract and format all text from this image.",
                        },
                    ],
                },
            ],
        )

        return message.content[0].text

    return _traced_ocr(image_url, reference)


def test_claude_models():
    # Get the first image URL for testing
    test_image = IMG_URLS[0]
    print(f"Testing with image: {test_image['name']}\n")

    # Filter for Claude models
    claude_models = [m for m in MODELS if m["provider"] == "claude"]

    for model in claude_models:
        print(f"\nTesting {model['name']}")
        print("-" * 30)
        try:
            result = get_ocr_claude(
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
    test_claude_models()
