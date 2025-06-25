from agents import Agent, Runner
from agents.mcp import MCPServerSse
from logging_utils import LoggingUtils
from typing import List


class JobFinderAgent:
    def __init__(self, mcp_servers: List[MCPServerSse], verbose: bool = False):
        self.mcp_servers = mcp_servers
        self.verbose = verbose
        self.logger = LoggingUtils(verbose)

        self.agent = Agent(
            name="Job Finder Assistant",
            instructions="""You are a helpful job finding assistant. You will:
            1. Ask the user to describe what kind of job they want
            2. Use the firecrawl_scrape tool to scrape the Hacker News jobs page at https://news.ycombinator.com/jobs
            3. Analyze the scraped content to find 1 best fitting job
            4. Identify the most fitting job based on the user's description
            5. If you find a specific job URL, scrape that page for more details
            6. Finally present the job information to the user in a clear, concise manner (1 short paragraph, in bulletpoints)
            
            Before and after each step in the process (run), say a few words about what you're looking for/or have seen.
            
            Don't have to ask user throughout the process.
            If tool calling fails, please try again.
            Do not stop until you've provided the user with the actual job's description from the job page
            Stick to 1 final job.
            """,
            mcp_servers=mcp_servers,
            model="gpt-4o",
        )

    async def find_answer(self, user_input: str):
        prompt = f"""The user is looking for: {user_input}
        
        Please help them find a suitable job from Hacker News jobs page. Start by scraping https://news.ycombinator.com/jobs"""

        self.logger.print_searching("Job Finder Agent")

        result = Runner.run_streamed(
            starting_agent=self.agent, input=prompt, max_turns=10)

        await self.logger.stream_results(result)

        self.logger.print_complete()
