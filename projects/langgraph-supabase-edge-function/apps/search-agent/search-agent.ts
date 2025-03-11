import { randomUUID } from "crypto";
import readline from "readline";
import fetch from "node-fetch";
import { stdin as processStdin, stdout as processStdout } from "process";
import { AUTH_TOKEN, EDGE_FUNCTION_URL } from "./consts.ts";

// Create readline interface for user input
const rl = readline.createInterface({
  input: processStdin,
  output: processStdout,
});

// Define response type
interface AgentResponse {
  response: string;
  steps: string[];
  threadId: string;
}

// Initialize thread ID
let currentThreadId = randomUUID();

async function callSearchAgent(query: string, threadId: string) {
  try {
    console.log(`Sending query: "${query}"...`);
    console.log(`Thread ID: ${threadId}`);

    const response = await fetch(EDGE_FUNCTION_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${AUTH_TOKEN}`,
      },
      body: JSON.stringify({ query, threadId }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Error from server (${response.status}): ${errorText}`);
    }

    const result = (await response.json()) as AgentResponse;

    // Update the thread ID in case the server created a new one
    if (result.threadId) {
      currentThreadId = result.threadId;
    }

    console.log("\n----- SEARCH AGENT RESPONSE -----");
    console.log(`Thread ID: ${currentThreadId}`);
    console.log(`Answer: ${result.response}`);

    console.log("\nProcess Steps:");
    result.steps.forEach((step: string, index: number) => {
      console.log(`${index + 1}. ${step}`);
    });

    console.log("---------------------------------\n");
  } catch (error: unknown) {
    console.error(
      "Failed to get response:",
      error instanceof Error ? error.message : String(error)
    );
  }
}

function startCLI() {
  console.log("🔍 Search Agent CLI");
  console.log(`Initial Thread ID: ${currentThreadId}`);
  console.log(
    'Type your query, "new_thread" to start a new conversation, or "exit" to quit\n'
  );

  function promptUser() {
    rl.question("> ", async (query: string) => {
      if (query.toLowerCase() === "exit") {
        console.log("Goodbye!");
        rl.close();
        return;
      }

      if (query.toLowerCase() === "new_thread") {
        currentThreadId = randomUUID();
        console.log(`Started new thread with ID: ${currentThreadId}`);
        promptUser();
        return;
      }

      if (query.trim()) {
        await callSearchAgent(query, currentThreadId);
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
