from utils import get_ocr_result
from consts import MODELS, IMG_URLS


def run_ocr_battle():
    for img_data in IMG_URLS:
        print(f"\nProcessing image: {img_data['name']}")
        print("-" * 50)

        # Load ground truth if needed
        with open(img_data["ground_truth_file_name"], "r") as f:
            ground_truth = f.read()

        for model in MODELS:
            print(f"\nUsing {model['provider']} - {model['name']}")
            try:
                result = get_ocr_result(
                    img_data["url"], model["provider"], model["name"], img_data["name"]
                )
                print(f"Result:\n{result}\n")
                # Compare with ground truth here if needed
            except Exception as e:
                print(f"Error: {str(e)}")

        print("=" * 50)


if __name__ == "__main__":
    run_ocr_battle()
