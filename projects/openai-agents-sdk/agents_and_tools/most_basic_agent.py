import sys
from agents import Agent, Runner
from dotenv import load_dotenv
from agents import set_default_openai_key
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
set_default_openai_key(openai_api_key)


agent = Agent(
    name="Assistant", instructions="You are sassy code instructor", model="gpt-4o"
)

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")

print(result.final_output)
