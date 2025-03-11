require("dotenv").config();

const { openai } = require("@ai-sdk/openai");
const { streamText } = require("ai");

// Make sure you have OPENAI_API_KEY set in your environment
if (!process.env.OPENAI_API_KEY) {
  console.error("Error: OPENAI_API_KEY environment variable is not set");
  process.exit(1);
}

async function generateText() {
  try {
    console.log("Generating text, please wait...");

    const prompt =
      process.argv[2] || "Write a short poem about artificial intelligence";
    console.log(`Prompt: "${prompt}"`);
    console.log("Response:");

    const result = streamText({
      model: openai("gpt-4o"),
      prompt,
    });

    // Handle the text stream
    for await (const chunk of result.textStream) {
      // Print each chunk as it arrives
      process.stdout.write(chunk);
    }

    console.log("\n\nGeneration complete!");
  } catch (error) {
    console.error("Error generating text:", error);
  }
}

// Run the function
generateText();
