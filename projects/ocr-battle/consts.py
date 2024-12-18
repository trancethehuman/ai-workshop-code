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
]

IMG_URLS = [
    "https://github.com/trancethehuman/ai-workshop-code/blob/main/projects/ocr-battle/data/cleaned/seven-points-of-failure-in-rag.png?raw=true",
    "https://github.com/trancethehuman/ai-workshop-code/blob/main/projects/ocr-battle/data/cleaned/attention-is-all-you-need.png?raw=true",
    "https://github.com/trancethehuman/ai-workshop-code/blob/main/projects/ocr-battle/data/cleaned/attention-is-all-you-need-upside-down.png?raw=true",
    "https://github.com/trancethehuman/ai-workshop-code/blob/main/projects/ocr-battle/data/cleaned/bill-gates-resume.png?raw=true",
    "https://github.com/trancethehuman/ai-workshop-code/blob/main/projects/ocr-battle/data/cleaned/code-screenshot.png?raw=true",
    "https://github.com/trancethehuman/ai-workshop-code/blob/main/projects/ocr-battle/data/cleaned/code-left-pdf-right.png?raw=true",
]
