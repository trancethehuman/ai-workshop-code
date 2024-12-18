def load_ground_truth(filename: str) -> str:
    try:
        with open(f"data/ground_truths/{filename}.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find {filename}.txt ground truth file")


# Load ground truth texts
seven_points_of_failure_in_rag = load_ground_truth("seven-points-of-failure-in-rag")
attention_is_all_you_need = load_ground_truth("attention-is-all-you-need")
attention_is_all_you_need_upside_down = load_ground_truth(
    "attention-is-all-you-need-upside-down"
)

# Make variable available for import
__all__ = ["seven_points_of_failure_in_rag"]

# TEST
if __name__ == "__main__":
    print(seven_points_of_failure_in_rag)
