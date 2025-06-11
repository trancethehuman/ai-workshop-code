from pydantic import BaseModel
from agents import (
    Agent,
    GuardrailFunctionOutput,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    output_guardrail,
)


class RelevanceCheckOutput(BaseModel):
    is_irrelevant: bool
    reasoning: str
    topic_detected: str


@output_guardrail
async def bootcamp_relevance_guardrail(
    ctx: RunContextWrapper, agent: Agent, output: str
) -> GuardrailFunctionOutput:
    """
    Output guardrail that checks if the response is relevant to the agent engineering bootcamp.
    Triggers tripwire if the output is about irrelevant topics like math, stock prices, etc.
    """

    guardrail_agent = Agent(
        name="Relevance Guardrail",
        instructions="""You are a relevance checker for an Agent Engineering Bootcamp Teaching Assistant.
        
        Check if the output is relevant to the agent engineering bootcamp topics such as:
        - Agent development and engineering
        - MCP (Model Context Protocol) setup and usage
        - Bootcamp schedule, curriculum, or logistics
        - Programming concepts related to agent development
        - AI/ML concepts relevant to agent engineering
        
        The output is IRRELEVANT if it's about topics like:
        - Math homework or math problems unrelated to agent engineering
        - Stock prices or financial advice
        - General trivia or facts unrelated to agent engineering
        - Personal advice unrelated to the bootcamp
        - Other technical topics not related to agent engineering
        
        Be strict but fair - programming examples that demonstrate agent concepts are relevant,
        but general programming help unrelated to agents is not.""",
        output_type=RelevanceCheckOutput,
    )

    result = await Runner.run(
        guardrail_agent,
        f"Check if this output is relevant to agent engineering bootcamp: {output}",
        context=ctx.context
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_irrelevant,
    )
