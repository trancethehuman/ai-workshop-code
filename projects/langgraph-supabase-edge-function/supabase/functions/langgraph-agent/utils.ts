// Utility functions for LangGraph Agent

/**
 * Extracts plain text from a MessageContent object from LangChain
 * Handles different formats that MessageContent might have (string, array, object)
 */
export const getTextFromContent = (content: any): string => {
  if (typeof content === "string") {
    return content;
  } else if (Array.isArray(content)) {
    // Extract text from array of content blocks
    return content
      .filter((item) => item.type === "text")
      .map((item) => item.text)
      .join("\n");
  } else if (content && typeof content === "object" && "text" in content) {
    return content.text;
  }
  return String(content || "");
};
