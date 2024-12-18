OCR_SYSTEM_PROMPT = """You're an expert at OCR and you extract the content from images, website and PDFs verbatim. Your response must be in markdown format (with proper headers). Do not include information that is not in the image.

If there are charts, make sure to draw them in markdown friendly format.

If there're tables, make sure they're in markdown format as well."""

MODELS = [
    {"provider": "google", "name": "gemini-1.5-flash-8b", "function": "get_ocr_gemini"},
    {"provider": "google", "name": "gemini-1.5-flash", "function": "get_ocr_gemini"},
    {"provider": "google", "name": "gemini-1.5-pro", "function": "get_ocr_gemini"},
    {
        "provider": "google",
        "name": "gemini-2.0-flash-exp",
        "function": "get_ocr_gemini",
    },
    {
        "provider": "llama",
        "name": "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        "function": "get_ocr_llama",
    },
    {
        "provider": "llama",
        "name": "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        "function": "get_ocr_llama",
    },
    {
        "provider": "claude",
        "name": "claude-3-5-sonnet-20241022",
        "function": "get_ocr_claude",
    },
    {
        "provider": "openai",
        "name": "gpt-4o-2024-11-20",
        "function": "get_ocr_openai",
    },
    {
        "provider": "openai",
        "name": "gpt-4o-mini-2024-07-18",
        "function": "get_ocr_openai",
    },
    {
        "provider": "x",
        "name": "grok-2-vision-1212",
        "function": "get_ocr_x",
    },
]

IMG_URLS = [
    {
        "name": "seven-points-of-failure-in-rag.png",
        "url": "https://github.com/trancethehuman/ai-workshop-code/blob/main/projects/ocr-battle/data/cleaned/seven-points-of-failure-in-rag.png?raw=true",
        "ground_truth_file_name": "./ground_truths/seven-points-of-failure-in-rag.txt",
    },
    {
        "name": "attention-is-all-you-need.png",
        "url": "https://github.com/trancethehuman/ai-workshop-code/blob/main/projects/ocr-battle/data/cleaned/attention-is-all-you-need.png?raw=true",
        "ground_truth_file_name": "./ground_truths/attention-is-all-you-need.txt",
    },
    {
        "name": "attention-is-all-you-need-upside-down.png",
        "url": "https://github.com/trancethehuman/ai-workshop-code/blob/main/projects/ocr-battle/data/cleaned/attention-is-all-you-need-upside-down.png?raw=true",
        "ground_truth_file_name": "./ground_truths/attention-is-all-you-need-upside-down.txt",
    },
    {
        "name": "bill-gates-resume.png",
        "url": "https://github.com/trancethehuman/ai-workshop-code/blob/main/projects/ocr-battle/data/cleaned/bill-gates-resume.png?raw=true",
        "ground_truth_file_name": "./ground_truths/bill-gates-resume.txt",
    },
    {
        "name": "code-screenshot.png",
        "url": "https://github.com/trancethehuman/ai-workshop-code/blob/main/projects/ocr-battle/data/cleaned/code-screenshot.png?raw=true",
        "ground_truth_file_name": "./ground_truths/code-screenshot.txt",
    },
    {
        "name": "code-left-pdf-right.png",
        "url": "https://github.com/trancethehuman/ai-workshop-code/blob/main/projects/ocr-battle/data/cleaned/code-left-pdf-right.png?raw=true",
        "ground_truth_file_name": "./ground_truths/code-left-pdf-right.txt",
    },
]
