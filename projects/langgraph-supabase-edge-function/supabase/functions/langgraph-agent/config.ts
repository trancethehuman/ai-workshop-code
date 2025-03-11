// Configuration settings for the LangGraph Agent
// Centralizes environment variable access and configuration

/**
 * Gets required API keys from environment variables
 * @returns Object containing API keys
 * @throws Error if any required API key is missing
 */
export const getApiKeys = () => {
  const OPENAI_API_KEY = Deno.env.get("OPENAI_API_KEY");
  const TAVILY_API_KEY = Deno.env.get("TAVILY_API_KEY");

  if (!OPENAI_API_KEY || !TAVILY_API_KEY) {
    throw new Error("Required API keys not configured");
  }

  return {
    OPENAI_API_KEY,
    TAVILY_API_KEY,
  };
};

// Model configuration settings
export const MODEL_CONFIG = {
  temperature: 0,
  model: "gpt-4o-mini",
};

// Search tool configuration
export const SEARCH_CONFIG = {
  maxResults: 5,
};
