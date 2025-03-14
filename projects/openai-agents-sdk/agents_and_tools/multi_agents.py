import asyncio

from models.sales import SalesContext
from prompts.sales import (
    COLD_EMAIL_SPECIALIST_INSTRUCTIONS,
    SALES_DEVELOPMENT_REP_INSTRUCTIONS,
    SALES_TEAM_LEAD_INSTRUCTIONS,
)

from agents import Agent, RunContextWrapper, RunResult, Runner, handoff
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions

from agent_tools.scrape_and_extract_linkedin_profile import extract_linkedin_profile
from agent_tools.tool_generate_outbound_email import generate_email
from data.sales_leads import leads
from miscs.run_parallel_agents import run_dict_tasks_in_parallel


async def on_handoff_callback(ctx: RunContextWrapper[SalesContext]):
    print("\n🔄 Handoff just happened")


# AGENTs
sales_team_lead = Agent[SalesContext](
    name="Sales Team Lead",
    instructions=prompt_with_handoff_instructions(SALES_TEAM_LEAD_INSTRUCTIONS),
    model="gpt-4o",
)

sales_development_rep = Agent[SalesContext](
    name="Sales Development Rep",
    instructions=prompt_with_handoff_instructions(SALES_DEVELOPMENT_REP_INSTRUCTIONS),
    tools=[extract_linkedin_profile],
    model="gpt-4o",
)

cold_email_specialist = Agent[SalesContext](
    name="Cold Email Specialist",
    instructions=prompt_with_handoff_instructions(COLD_EMAIL_SPECIALIST_INSTRUCTIONS),
    tools=[generate_email],
    model="gpt-4o",
)

sales_team_lead.handoffs = [
    handoff(agent=sales_development_rep, on_handoff=on_handoff_callback),
    handoff(agent=cold_email_specialist, on_handoff=on_handoff_callback),
]
sales_development_rep.handoffs = [
    handoff(agent=sales_team_lead, on_handoff=on_handoff_callback)
]
cold_email_specialist.handoffs = [
    handoff(agent=sales_team_lead, on_handoff=on_handoff_callback)
]


async def process_sales_lead(lead: dict) -> RunResult:
    """Process a sales lead through the multi-agent workflow"""
    name = lead["name"]
    linkedin_url = lead["linkedin_url"]

    context: SalesContext = {
        "name": name,
        "linkedin_url": linkedin_url,
        "profile_data": None,
        "email_draft": None,
    }

    print(f"\n🔍 Processing lead: {name} ({linkedin_url})")

    final_result = await Runner.run(
        starting_agent=sales_team_lead,
        input=f"We have a new lead: {name} ({linkedin_url}). Please coordinate the process to research this lead and create a personalized outreach email.",
        context=context,
        max_turns=15,
    )

    return final_result


def display_lead_result(lead: dict, final_result: RunResult):
    print("Final results:")
    print(f"""
    Input: {final_result.input}
    Final message from agent: {final_result.final_output}
    Last agent: {final_result.last_agent.name}
    """)


async def process_multiple_leads_in_parallel():
    """Process a list of predefined leads in parallel"""
    print("\n===== Sales Outreach Multi-Agent System =====")

    results = await run_dict_tasks_in_parallel(
        process_function=process_sales_lead,
        input_dicts=leads,
        show_progress=True,
        result_handler=display_lead_result,
    )

    return results


def main():
    """Main entry point for the application"""
    print("Starting Sales Outreach Multi-Agent System...")
    asyncio.run(process_multiple_leads_in_parallel())


if __name__ == "__main__":
    main()
