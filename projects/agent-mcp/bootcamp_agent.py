from agents import Agent, Runner
from agents.mcp import MCPServerSse
from logging_utils import LoggingUtils
from typing import List, Optional


class BootcampAgent:
    def __init__(self, mcp_servers: List[MCPServerSse], verbose: bool = False, output_guardrails: Optional[List] = None):
        self.mcp_servers = mcp_servers
        self.verbose = verbose
        self.logger = LoggingUtils(verbose)

        self.agent = Agent(
            name="Agent Engineering Bootcamp Teaching Assistant",
            instructions="""You are a helpful teaching assistant to an agent engineering bootcamp
            If user asks about how to setup the bootcamp's MCP server, send them this link: https://agent-engineering-bootcamp-mcp.vercel.app
            """,
            mcp_servers=mcp_servers,
            model="gpt-4o",
            output_guardrails=output_guardrails or [],
        )

    async def find_answer(self, user_input: str):
        prompt = f"""The user is looking for: {user_input}
        """

        self.logger.print_searching("Bootcamp Teaching Assistant")

        result = Runner.run_streamed(
            starting_agent=self.agent, input=prompt, max_turns=10)

        await self.logger.stream_results(result)

        self.logger.print_complete()
