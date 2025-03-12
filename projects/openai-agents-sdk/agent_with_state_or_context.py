import asyncio

from agents import (
    Agent,
    Runner,
)

from prompts import FOUNDER_AGENT_INSTRUCTIONS
from tools.tavily_search import tavily_search
from tools.retrieve_founder_articles import search_founder_articles
from agent_context import AgentContext
from agent_logger import AgentLifecycleLogger, AgentLogger, MinimalLogger
from utils import setup_logging, load_api_keys

logger = setup_logging()
load_api_keys()

AgentLogger.configure(enabled=True, log_level="INFO")


founder_agent = Agent[AgentContext](
    name="Founder Knowledge Assistant",
    instructions=FOUNDER_AGENT_INSTRUCTIONS,
    tools=[
        search_founder_articles,
        tavily_search,
    ],
    model="gpt-4o",
)


async def run_agent_with_query(
    query: str, context: AgentContext, verbose_logging: bool = False
):
    """Run the agent with a query, using the provided context"""

    # Create lifecycle logger - use full logger if verbose, minimal otherwise
    lifecycle_logger = (
        AgentLifecycleLogger(enabled=verbose_logging)
        if verbose_logging
        else MinimalLogger(enabled=False)
    )

    # Run the agent with the query and context
    result = await Runner.run(
        starting_agent=founder_agent,
        input=query,
        context=context,
        hooks=lifecycle_logger,
    )

    print("\n=== RESPONSE ===")
    print(result.final_output)

    # Display the source information
    if context.last_tool_used == "founder_articles":
        print("\n[Source: Retrieved from founder articles database]")
    elif context.last_tool_used == "tavily_search":
        print("\n[Source: Retrieved from web search]")
    else:
        print("\n[Source: No external tools used]")

    return result


async def interactive_agent_loop(verbose_logging: bool = False):
    """Run the agent in an interactive loop with persistent context"""

    # Create a single context instance that persists across interactions
    context = (
        AgentContext()
    )  # this is basically our agent's state that gets passed from step to step

    print("\n=== Founder Knowledge Assistant ===")
    print(
        "Ask questions about founders. Type 'exit', 'quit', or 'q' to end the conversation."
    )
    print("Your context and conversation history will be maintained until you exit.")

    while True:
        query = input("\nYour question: ")

        # Check for exit commands
        if query.lower() in ["exit", "quit", "q"]:
            print("Ending conversation. Goodbye!")
            break

        # Run the agent with the current query and the persistent context
        await run_agent_with_query(query, context, verbose_logging)

        # Optionally show context state after each interaction
        if verbose_logging:
            print("\n=== CURRENT CONTEXT STATE ===")
            print(f"Recent searches: {context.recent_searches}")
            print(f"Number of documents retrieved: {len(context.recent_documents)}")


def main():
    # Ask if verbose logging is wanted - only once at the beginning
    verbose_input = input("Enable verbose logging? (y/n, default: n): ").lower()
    verbose_logging = verbose_input == "y" or verbose_input == "yes"

    # Run the interactive loop
    asyncio.run(interactive_agent_loop(verbose_logging))


if __name__ == "__main__":
    main()
