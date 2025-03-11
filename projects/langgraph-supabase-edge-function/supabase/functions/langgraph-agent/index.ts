// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

// Setup type definitions for built-in Supabase Runtime APIs
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

// Import necessary packages for a direct implementation
import { TavilySearchResults } from "npm:@langchain/community@0.0.27/tools/tavily_search";
import { ChatOpenAI } from "npm:@langchain/openai@0.0.14";

import { getApiKeys, MODEL_CONFIG, SEARCH_CONFIG } from "./config.ts";
import { runAgent } from "./agent.ts";
import { getConversationState, saveConversationState } from "./db.ts";

// Log when the function is initialized
console.log("LangGraph Agent function initialized!");

const handler = async (req: Request): Promise<Response> => {
  try {
    // Get API keys from environment variables
    let apiKeys;
    try {
      apiKeys = getApiKeys();
    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Parse the request body
    const { query, threadId } = await req.json();

    if (!query) {
      return new Response(JSON.stringify({ error: "Query is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (!threadId) {
      return new Response(JSON.stringify({ error: "ThreadId is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Create a search tool
    const searchTool = new TavilySearchResults({
      apiKey: apiKeys.TAVILY_API_KEY,
      maxResults: SEARCH_CONFIG.maxResults,
    });

    // Create OpenAI chat model
    const model = new ChatOpenAI({
      openAIApiKey: apiKeys.OPENAI_API_KEY,
      temperature: MODEL_CONFIG.temperature,
      modelName: MODEL_CONFIG.model,
    });

    // Retrieve the conversation state from database
    const state = await getConversationState(threadId);

    // Run the agent logic with state from database
    const result = await runAgent(query, model, searchTool, state);

    // Save the updated state to database
    await saveConversationState(threadId, result.state);

    // Return agent's response, but don't include state in response anymore
    const response = {
      ...result.output,
      threadId,
    };

    // Return the agent's response
    return new Response(JSON.stringify(response), {
      headers: {
        "Content-Type": "application/json",
        Connection: "keep-alive",
      },
    });
  } catch (error) {
    console.error("Error processing request:", error);
    return new Response(
      JSON.stringify({ error: error.message, stack: error.stack }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
};

// Use Deno.serve for Supabase Edge Functions
Deno.serve(handler);

/* To invoke locally:

  1. Run `supabase start` (see: https://supabase.com/docs/reference/cli/supabase-start)
  2. Make an HTTP request:

  curl -i --location --request POST 'http://127.0.0.1:54321/functions/v1/langgraph-agent' \
    --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0' \
    --header 'Content-Type: application/json' \
    --data '{"query":"what is the weather in San Francisco?"}'

*/
