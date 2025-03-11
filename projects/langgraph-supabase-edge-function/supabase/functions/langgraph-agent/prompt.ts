import { TavilySearchResults } from "npm:@langchain/community@0.0.27/tools/tavily_search";

/**
 * Creates a prompt for the planning stage
 * @param query The user's query
 * @param history Previous conversation history
 * @returns A formatted prompt string
 */
export function createPlanPrompt(
  query: string,
  history: Array<{ role: string; content: string }> = []
): string {
  // Format the conversation history
  const formattedHistory = formatConversationHistory(history);

  return `You are a helpful search assistant. Your goal is to provide accurate information to the user's queries.

${formattedHistory ? `Previous conversation:\n${formattedHistory}\n\n` : ""}

Current query: ${query}

First, decide if you need to search for information or if you can answer directly from your knowledge.

If you need to search for information:
- Respond with "SEARCH: <search query>" where <search query> is an optimized search query based on the user's question.
- Always craft a new, specific search query that incorporates context from previous interactions.
- Your search query should be different from the user's exact words - reformulate it to get better search results.
- If this is a follow-up question, make sure your search query includes relevant context from the conversation.
- Make sure your search query is specific, relevant, and likely to return useful results.

If you can answer directly without a search:
- Respond with "ANSWER: <your answer>" where <your answer> is your direct response to the user's query.

Only respond with either SEARCH or ANSWER as described above.`;
}

/**
 * Creates a prompt for generating the final answer
 * @param query The user's query
 * @param searchResults Results from the search
 * @param history Previous conversation history
 * @returns A formatted prompt string
 */
export function createAnswerPrompt(
  query: string,
  searchResults: any,
  history: Array<{ role: string; content: string }> = []
): string {
  // Format the conversation history
  const formattedHistory = formatConversationHistory(history);

  return `You are a helpful search assistant. Your goal is to provide accurate information to the user's queries.

${formattedHistory ? `Previous conversation:\n${formattedHistory}\n\n` : ""}

Current query: ${query}

I searched for information and found the following results:
${JSON.stringify(searchResults, null, 2)}

Based on these search results, provide a comprehensive and accurate answer to the user's query. 
Include relevant facts and information from the search results.

If this is a follow-up question, make sure your answer builds upon previous information shared in the conversation.
Connect new information with what was previously discussed when relevant.

If the search results don't contain enough information to answer the query confidently, acknowledge the limitations of your response.
Avoid making up information that isn't supported by the search results.`;
}

/**
 * Formats conversation history into a readable string
 * @param history Array of conversation messages
 * @returns Formatted history string
 */
function formatConversationHistory(
  history: Array<{ role: string; content: string }>
): string {
  if (!history || history.length <= 1) {
    return "";
  }

  // Skip the most recent user query as it's handled separately
  const relevantHistory = history.slice(0, -1);

  return relevantHistory
    .map((msg) => {
      const role = msg.role === "user" ? "User" : "Assistant";
      return `${role}: ${msg.content}`;
    })
    .join("\n");
}

export function getTextFromContent(content: any): string {
  if (typeof content === "string") {
    return content;
  } else if (Array.isArray(content)) {
    return content
      .map((item) => {
        if (typeof item === "string") {
          return item;
        } else if (item.type === "text") {
          return item.text;
        }
        return "";
      })
      .join(" ");
  } else if (content.type === "text") {
    return content.text;
  }
  return String(content);
}
