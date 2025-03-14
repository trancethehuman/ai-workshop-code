from dataclasses import dataclass

import os
from typing import Any, Dict, Optional
from agents import RunContextWrapper, function_tool
from dotenv import load_dotenv
from openai import OpenAI
import requests
from agent_tools.utils.linkedin import parse_linkedin_profile

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
scraper_api_key = os.environ.get("SCRAPER_API_KEY")


client = OpenAI(api_key=openai_api_key)
