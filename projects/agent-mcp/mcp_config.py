import os
from agents.mcp import MCPServerSse, MCPServerStdio
from typing import Dict


class MCPConfig:
    def __init__(self):
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.firecrawl_api_key:
            raise ValueError(
                "FIRECRAWL_API_KEY environment variable is not set")

        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not self.tavily_api_key:
            raise ValueError(
                "TAVILY_API_KEY environment variable is not set")

        self.firecrawl_url = f"https://mcp.firecrawl.dev/{self.firecrawl_api_key}/sse"
        self.bootcamp_url = "https://agent-engineering-bootcamp-mcp.vercel.app/sse"

    def get_firecrawl_params(self):
        return {
            "url": self.firecrawl_url,
        }

    def get_bootcamp_params(self):
        return {
            "url": self.bootcamp_url,
        }

    def get_tavily_params(self):
        return {
            "command": "npx",
            "args": ["-y", "tavily-mcp@0.2.4"],
            "env": {"TAVILY_API_KEY": self.tavily_api_key}
        }

    async def create_servers(self):
        firecrawl_server = MCPServerSse(
            cache_tools_list=True,
            name="Firecrawl MCP",
            params=self.get_firecrawl_params(),
            client_session_timeout_seconds=60
        )

        bootcamp_server = MCPServerSse(
            cache_tools_list=True,
            name="Agent Engineering Bootcamp MCP",
            params=self.get_bootcamp_params(),
            client_session_timeout_seconds=15
        )

        tavily_server = MCPServerStdio(
            cache_tools_list=True,
            name="Tavily MCP",
            params=self.get_tavily_params(),
        )

        return {
            "firecrawl": firecrawl_server,
            "bootcamp": bootcamp_server,
            "tavily": tavily_server
        }
