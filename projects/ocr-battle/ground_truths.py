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
bill_gates_resume = load_ground_truth("bill-gates-resume")
code_left_pdf_right = load_ground_truth("code-left-pdf-right")
code_screenshot = load_ground_truth("code-screenshot")

# Make variables available for import
__all__ = [
    "seven_points_of_failure_in_rag",
    "attention_is_all_you_need",
    "attention_is_all_you_need_upside_down",
    "bill_gates_resume",
    "code_left_pdf_right",
    "code_screenshot",
]

# TEST
if __name__ == "__main__":
    print(seven_points_of_failure_in_rag)
