import { TavilySearchResults } from "npm:@langchain/community@0.0.27/tools/tavily_search";
import { ChatOpenAI } from "npm:@langchain/openai@0.0.14";
import { HumanMessage } from "npm:@langchain/core@0.1.17/messages";
import { getTextFromContent } from "./utils.ts";
import { createPlanPrompt, createAnswerPrompt } from "./prompt.ts";

// Define conversation state type
interface ConversationState {
  history: Array<{ role: string; content: string }>;
}

/**
 * Runs the agent with a query
 * @param query User query to process
 * @param model ChatOpenAI instance
 * @param searchTool TavilySearchResults instance
 * @param state Previous conversation state (if any)
 * @returns Object containing final answer, steps taken, and updated state
 */
export async function runAgent(
  query: string,
  model: ChatOpenAI,
  searchTool: TavilySearchResults,
  state?: ConversationState
) {
  // Array to track agent steps for debugging/visibility
  const steps: string[] = [];
  let finalAnswer = "";

  // Initialize conversation history from state or create new
  const history = state?.history || [];

  // Add the current query to the history
  history.push({ role: "user", content: query });
  steps.push("Received user query");

  // First, decide if we need to search or can answer directly
  steps.push("Planning approach to answer query");
  const planPrompt = createPlanPrompt(query, history);

  const planResponse = await model.invoke([new HumanMessage(planPrompt)]);
  const planResponseText = getTextFromContent(planResponse.content);
  steps.push("Determined approach to answer");

  // Add the plan response to history
  history.push({
    role: "assistant",
    content: planResponseText,
  });

  if (planResponseText.startsWith("SEARCH:")) {
    // Extract the search query
    const searchQuery = planResponseText.substring(8).trim();
    steps.push(`Searching for: ${searchQuery}`);

    // Perform the search
    const searchResults = await searchTool.invoke(searchQuery);
    console.log("Search results:", searchResults);
    steps.push("Received search results");

    // Generate final answer using the search results
    const answerPrompt = createAnswerPrompt(query, searchResults, history);
    const answerResponse = await model.invoke([new HumanMessage(answerPrompt)]);

    finalAnswer = getTextFromContent(answerResponse.content);
    steps.push("Generated answer from search results");

    // Add the final answer to history
    history.push({
      role: "assistant",
      content: finalAnswer,
    });
  } else {
    // Direct answer without search
    const responseText = getTextFromContent(planResponse.content);
    finalAnswer = responseText.startsWith("ANSWER:")
      ? responseText.substring(8).trim()
      : responseText;
    steps.push("Provided direct answer without search");
  }

  // Return final answer, steps, and updated state
  return {
    output: {
      response: finalAnswer,
      steps: steps,
    },
    state: {
      history: history,
    },
  };
}
