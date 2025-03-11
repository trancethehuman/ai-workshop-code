import readline from "readline";
import fetch from "node-fetch";

// Configuration
const EDGE_FUNCTION_URL = "http://127.0.0.1:54321/functions/v1/langgraph-agent";
const AUTH_TOKEN =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0";

// Create readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

async function callSearchAgent(query: string) {
  try {
    console.log(`Sending query: "${query}"...`);

    const response = await fetch(EDGE_FUNCTION_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${AUTH_TOKEN}`,
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Error from server (${response.status}): ${errorText}`);
    }

    const result = await response.json();

    console.log("\n----- SEARCH AGENT RESPONSE -----");
    console.log(`Answer: ${result.response}`);

    console.log("\nProcess Steps:");
    result.steps.forEach((step: string, index: number) => {
      console.log(`${index + 1}. ${step}`);
    });

    console.log("---------------------------------\n");
  } catch (error) {
    console.error("Failed to get response:", error.message);
  }
}

function startCLI() {
  console.log("🔍 Search Agent CLI");
  console.log('Type your query or "exit" to quit\n');

  function promptUser() {
    rl.question("> ", async (query) => {
      if (query.toLowerCase() === "exit") {
        console.log("Goodbye!");
        rl.close();
        return;
      }

      if (query.trim()) {
        await callSearchAgent(query);
      }

      promptUser();
    });
  }

  promptUser();
}

// Start the CLI
startCLI();

// Note: To run this script, ensure you have the required packages installed:
// npm install readline node-fetch
// Then run with: node search-agent.js
