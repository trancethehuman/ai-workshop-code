from agents import Agent, Runner
from agents.mcp import MCPServerStdio
from logging_utils import LoggingUtils
from typing import List


class WebSearchAgent:
    def __init__(self, mcp_servers: List[MCPServerStdio], verbose: bool = False):
        self.mcp_servers = mcp_servers
        self.verbose = verbose
        self.logger = LoggingUtils(verbose)

        self.agent = Agent(
            name="Web Search Assistant",
            instructions="""You are a helpful web search assistant. You can:
            1. Search the web for any topic using Tavily's search capabilities
            2. Find recent news articles and information
            3. Extract and summarize content from web pages
            4. Provide comprehensive answers based on web search results
            
            Available tools:
            - tavily_search: For searching the web for information on any topic
            - tavily_extract: For extracting content from specific web pages
            
            Always provide clear, accurate, and up-to-date information based on your search results.
            If you can't find information on a topic, let the user know and suggest alternative search terms.
            """,
            mcp_servers=mcp_servers,
            model="gpt-4o",
        )

    async def find_answer(self, user_input: str):
        prompt = f"""The user is asking: {user_input}
        
        Please search the web to find relevant and up-to-date information to answer their question."""

        self.logger.print_searching("Web Search Assistant")

        result = Runner.run_streamed(
            starting_agent=self.agent, input=prompt, max_turns=10)

        await self.logger.stream_results(result)

        self.logger.print_complete()