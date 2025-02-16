import { generateText } from "ai";
import { google } from "@ai-sdk/google";

async function main() {
  const messages = [{ role: "user" as const, content: "Hello" }];

  // Get a language model
  const model = google("gemini-2.0-flash");

  // Call the language model with the prompt
  const result = await generateText({
    model,
    messages,
    maxTokens: 8192,
    temperature: 0.7,
    topP: 0.4,
  });

  console.log(result.text);
}

main().catch(console.error);
