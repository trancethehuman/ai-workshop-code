// Agent logic for the LangGraph Agent
import { TavilySearchResults } from "npm:@langchain/community@0.0.27/tools/tavily_search";
import { ChatOpenAI } from "npm:@langchain/openai@0.0.14";
import { HumanMessage } from "npm:@langchain/core@0.1.17/messages";
import { getTextFromContent } from "./utils.ts";

/**
 * Runs the agent with a query
 * @param query User query to process
 * @param model ChatOpenAI instance
 * @param searchTool TavilySearchResults instance
 * @returns Object containing final answer and steps taken
 */
export async function runAgent(
  query: string,
  model: ChatOpenAI,
  searchTool: TavilySearchResults
) {
  // Array to track agent steps for debugging/visibility
  const steps: string[] = [];
  let finalAnswer = "";

  // First, decide if we need to search or can answer directly
  steps.push("Planning approach to answer query");
  const planPrompt = `You are a helpful, truthful AI assistant.
Given the following query, decide if you need to search for information or if you can answer directly from your knowledge.
If you need to search, respond with "SEARCH: <search query>", where <search query> is a good search query for the question.
If you can answer directly, respond with "ANSWER: <your answer>".

Query: "${query}"`;

  const planResponse = await model.invoke([new HumanMessage(planPrompt)]);
  const planResponseText = getTextFromContent(planResponse.content);
  steps.push("Determined approach to answer");

  if (planResponseText.startsWith("SEARCH:")) {
    // Extract the search query
    const searchQuery = planResponseText.substring(8).trim();
    steps.push(`Searching for: ${searchQuery}`);

    // Perform the search
    const searchResults = await searchTool.invoke(searchQuery);
    console.log("Search results:", searchResults);
    steps.push("Received search results");

    // Generate final answer using the search results
    const answerResponse = await model.invoke([
      new HumanMessage(`Based on the following search results about "${query}":
${JSON.stringify(searchResults, null, 2)}

Please provide a comprehensive, accurate answer to the question: "${query}"
Include relevant information from the search results.`),
    ]);

    finalAnswer = getTextFromContent(answerResponse.content);
    steps.push("Generated answer from search results");
  } else {
    // Direct answer without search
    const responseText = getTextFromContent(planResponse.content);
    finalAnswer = responseText.startsWith("ANSWER:")
      ? responseText.substring(8).trim()
      : responseText;
    steps.push("Provided direct answer without search");
  }

  return {
    response: finalAnswer,
    steps: steps,
  };
}
