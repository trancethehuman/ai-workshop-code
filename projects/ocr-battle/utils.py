from typing import Dict, Any
from consts import MODELS
import importlib


def get_ocr_result(
    image_url: str, provider: str, model_name: str, image_name: str, reference: str
) -> str:
    """
    Get OCR result from specified provider and model
    """
    # Find the model config
    model_config = next(
        (m for m in MODELS if m["provider"] == provider and m["name"] == model_name),
        None,
    )

    if not model_config:
        raise ValueError(
            f"No model found for provider {provider} and name {model_name}"
        )

    # Import the corresponding module
    module = importlib.import_module(f"{provider}-ocr")

    # Get the function
    function = getattr(module, model_config["function"])

    # Call the function with image name as tag and reference
    return function(image_url, model_name, image_name, reference)
