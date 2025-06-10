import asyncio
import os
from dotenv import load_dotenv
from rich.prompt import Prompt

from agents import set_tracing_disabled
from agent import JobFinderAgent
from bootcamp_agent import BootcampAgent
from mcp_config import MCPConfig
from logging_utils import LoggingUtils

load_dotenv()
set_tracing_disabled(True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

VERBOSE = os.getenv("VERBOSE", "false").lower() in ["true", "1", "yes"]


async def main():
    logger = LoggingUtils(verbose=VERBOSE)
    logger.print_welcome("Bootcamp Teaching Assistant")

    try:
        mcp_config = MCPConfig()
        logger.print_connecting()

        servers = await mcp_config.create_servers()
        async with servers["firecrawl"] as firecrawl_server, servers["bootcamp"] as bootcamp_server:
            logger.print_connected()

            job_finder = JobFinderAgent(
                mcp_servers=[firecrawl_server, bootcamp_server], verbose=VERBOSE)
            bootcamp_agent = BootcampAgent(
                mcp_servers=[firecrawl_server, bootcamp_server], verbose=VERBOSE)

            while True:
                user_input = Prompt.ask(
                    "\n[bold green]What can I help you with today? (type 'quit' to exit)[/bold green]")

                if user_input.lower().strip() in ['quit', 'exit', 'q']:
                    logger.console.print(
                        "\n[bold yellow]Thanks for using Agent Playground! Goodbye! 👋[/bold yellow]")
                    break

                # await job_finder.find_job(user_input)
                await bootcamp_agent.find_answer(user_input)

    except ValueError as e:
        logger.console.print(f"[bold red]Error: {str(e)}[/bold red]")
        logger.console.print(
            "Please ensure FIRECRAWL_API_KEY is set in your .env file")
    except Exception as e:
        logger.console.print(
            f"[bold red]An unexpected error occurred: {str(e)}[/bold red]")


if __name__ == "__main__":
    asyncio.run(main())
