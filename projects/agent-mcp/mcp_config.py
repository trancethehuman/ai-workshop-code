import os
from agents.mcp import MCPServerSse


class MCPConfig:
    def __init__(self):
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.firecrawl_api_key:
            raise ValueError(
                "FIRECRAWL_API_KEY environment variable is not set")

        self.firecrawl_url = f"https://mcp.firecrawl.dev/{self.firecrawl_api_key}/sse"

    def get_server_params(self):
        return {
            "url": self.firecrawl_url,
        }

    async def create_server(self):
        return MCPServerSse(
            cache_tools_list=True,
            name="Firecrawl MCP",
            params=self.get_server_params(),
            client_session_timeout_seconds=15
        )
