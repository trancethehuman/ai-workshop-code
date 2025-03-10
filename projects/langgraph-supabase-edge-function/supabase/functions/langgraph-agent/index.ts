// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

// Setup type definitions for built-in Supabase Runtime APIs
import "jsr:@supabase/functions-js/edge-runtime.d.ts";

// Import necessary packages for a direct implementation
import { TavilySearchResults } from "npm:@langchain/community@0.0.27/tools/tavily_search";
import { ChatOpenAI } from "npm:@langchain/openai@0.0.14";
import { HumanMessage } from "npm:@langchain/core@0.1.17/messages";

// Log when the function is initialized
console.log("LangGraph Agent function initialized!");

const handler = async (req: Request): Promise<Response> => {
  try {
    // Get API keys from environment variables
    const OPENAI_API_KEY = Deno.env.get("OPENAI_API_KEY");
    const TAVILY_API_KEY = Deno.env.get("TAVILY_API_KEY");

    if (!OPENAI_API_KEY || !TAVILY_API_KEY) {
      return new Response(
        JSON.stringify({ error: "API keys not configured" }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    // Parse the request body
    const { query } = await req.json();

    if (!query) {
      return new Response(JSON.stringify({ error: "Query is required" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Create a search tool
    const searchTool = new TavilySearchResults({
      apiKey: TAVILY_API_KEY,
      maxResults: 3,
    });

    // Create OpenAI chat model
    const model = new ChatOpenAI({
      apiKey: OPENAI_API_KEY,
      temperature: 0,
      model: "gpt-3.5-turbo",
    });

    // Instead of using LangGraph, let's implement a simple agent flow manually
    // Step 1: Ask the LLM what to do based on the query
    const planResponse = await model.call([
      new HumanMessage(`You are a helpful assistant that can search the web for information. 
You have access to a search tool that can find current information.

Given this query: "${query}"

Do you need to search for information to answer it accurately?
If yes, please respond with "SEARCH: your search query"
If no, please respond with "ANSWER: your direct answer"`),
    ]);

    console.log("Plan response:", planResponse.content);
    let finalAnswer = "";
    const steps = ["Planning how to respond"];

    // Step 2: Check if we need to search
    if (
      typeof planResponse.content === "string" &&
      planResponse.content.startsWith("SEARCH:")
    ) {
      steps.push("Decided to search for information");

      // Extract the search query
      const searchQuery = planResponse.content.substring(8).trim();
      console.log("Searching for:", searchQuery);
      steps.push(`Searching for: ${searchQuery}`);

      // Perform the search
      const searchResults = await searchTool.invoke(searchQuery);
      console.log("Search results:", searchResults);
      steps.push("Received search results");

      // Generate final answer using the search results
      const answerResponse = await model.call([
        new HumanMessage(`Based on the following search results about "${query}":
${JSON.stringify(searchResults, null, 2)}

Please provide a comprehensive, accurate answer to the question: "${query}"
Include relevant information from the search results.`),
      ]);

      finalAnswer = answerResponse.content;
      steps.push("Generated answer from search results");
    } else {
      // Direct answer without search
      finalAnswer = planResponse.content.startsWith("ANSWER:")
        ? planResponse.content.substring(8).trim()
        : planResponse.content;
      steps.push("Provided direct answer without search");
    }

    // Return the agent's response
    return new Response(
      JSON.stringify({
        response: finalAnswer,
        steps: steps,
      }),
      {
        headers: {
          "Content-Type": "application/json",
          Connection: "keep-alive",
        },
      }
    );
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
    --header 'Content-Type: application/json' \
    --data '{"query":"what is the weather in San Francisco?"}'

*/
