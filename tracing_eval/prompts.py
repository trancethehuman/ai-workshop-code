system_prompt_article_summary = """Summarize the most important point of a news article effectively and concisely.

Ensure that the summary captures the core message of the article with a focus on the most relevant information. Avoid including unnecessary background details or unrelated context; concentrate solely on the primary point that a reader must know. Where needed, include a single, succinct piece of context that helps the reader understand the article’s significance.

# Steps

1. **Identify the Core Message**: Read the article to determine the single most important point or conclusion. 
2. **Remove Unnecessary Detail**: Strip away background, secondary stories, and minor details that do not contribute to the core message.
3. **Summarize Clearly**: Write a concise summary that captures the essence of the main point in a straightforward manner."""

system_prompt_what_companies_were_mentioned = """
Extract and summarize all companies and startups mentioned in the article, including details on why each company or startup was mentioned.

Be sure to:
- Clearly identify each company or startup mentioned.
- Explain the specific reasons each company was brought up, such as context or achievements.
- Provide concise summaries that highlight essential information without losing key points.

# Steps

1. **Identify Companies**: As you go through the article, extract the names of all companies and startups.
2. **Contextual Information**: For each company or startup, identify the reason(s) they were mentioned.
3. **Summarize**: Compile a brief, clear summary for each company, focusing on the key reasons for being mentioned.

# Output Format

- Provide your output in a bullet point list.
- Include the company name, followed by a summary of the key information, formatted as:
  
  **Company Name**: [Reason why the company was mentioned, with context].

# Example

- **Startup X**: Launched an innovative platform for remote learning that gained significant traction during the pandemic, prompting its mention in the article.
- **Company Y**: Mentioned for its recent funding round to expand globally, positioning itself as a competitor in the logistics space.
  
(If the article contains more companies, list them similarly using concise descriptions that are informative yet succinct.)
"""

system_prompt_json_companies = """
Extract the names of companies and startups along with the key reasons they are mentioned in the given text, and return them in a structured JSON object.

# Steps

1. **Identify Companies/Startups**: Extract the names of each company or startup mentioned in the provided text.
2. **Determine the Reasons**: Identify the reasons each company or startup is mentioned—this may include achievements, innovations, funding, partnerships, or any other notable activity.
3. **Construct a JSON Object**: Create a JSON object with the name of each company/startup as well as the associated reason extracted from the text.

# Output Format

The output should be a JSON object with each company or startup represented as an item in a list. Each item should have the following key-value pairs:
- `"name"`: The name of the company or startup.
- `"reason"`: The reason the company or startup is mentioned in the text.

```json
[
    {
        "name": "Company A",
        "reason": "The company recently launched an innovative AI product."
    },
    {
        "name": "Company B",
        "reason": "Secured Series B funding of $20 million for business expansion."
    }
]
```

# Notes

- Ensure that both the company name and the reason are captured accurately.
- If there are multiple reasons for the company being mentioned, combine them into a concise explanation for the `"reason"` field.
- If the reason is not explicitly stated, infer it from the context as accurately as possible."""
