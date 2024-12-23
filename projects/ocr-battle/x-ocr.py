from openai import OpenAI
from dotenv import load_dotenv
from langsmith import traceable
import os
from pydantic import BaseModel
from consts import IMG_URLS, OCR_SYSTEM_PROMPT, MODELS

load_dotenv()

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)


class OCRResponse(BaseModel):
    text: str


def get_ocr_x(image_url: str, model_name: str, image_name: str, reference: str) -> str:
    @traceable(name=model_name, run_type="llm", tags=[image_name])
    def _traced_ocr(url: str, reference: str) -> str:
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
                                "detail": "high",
                            },
                        },
                    ],
                },
            ],
            temperature=0,
            max_tokens=4096,
        )

        return response.choices[0].message.content

    return _traced_ocr(image_url, reference)


def test_x_models():
    # Get the first image URL for testing
    test_image = IMG_URLS[0]
    print(f"Testing with image: {test_image['name']}\n")

    # Filter for X models
    x_models = [m for m in MODELS if m["provider"] == "x"]

    for model in x_models:
        print(f"\nTesting {model['name']}")
        print("-" * 30)
        try:
            result = get_ocr_x(
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
    test_x_models()
