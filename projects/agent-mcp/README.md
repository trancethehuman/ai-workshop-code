# Agent MCP Platform

An AI-powered platform featuring two specialized agents built with OpenAI Agents SDK and Model Context Protocol (MCP) servers. Choose between a Job Finder Agent that scrapes Hacker News jobs or a Bootcamp Teaching Assistant for agent engineering support.

## What This Is

This project demonstrates how to build AI agents that integrate with external services through MCP servers. It features:

- **Job Finder Agent**: Scrapes Hacker News jobs and finds positions matching your preferences
- **Bootcamp Agent**: Teaching assistant for an agent engineering bootcamp with content guardrails
- **Interactive CLI**: Rich terminal interface with clickable links and real-time streaming
- **MCP Integration**: Connects to Firecrawl and Bootcamp MCP servers for extended capabilities

## Required API Keys

To run this project, you'll need:

1. **OpenAI API Key** - For the AI agents (GPT-4o)
   - Sign up at: https://platform.openai.com/
   - Get your API key from: https://platform.openai.com/api-keys

2. **Firecrawl API Key** - For web scraping capabilities
   - Sign up at: https://firecrawl.dev/
   - Get your API key from your dashboard

## Setup Instructions

1. **Clone and navigate to the project**:
   ```bash
   cd /path/to/agent-mcp
   ```

2. **Create environment file**:
   ```bash
   # Create .env file with your API keys
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   echo "FIRECRAWL_API_KEY=your_firecrawl_api_key_here" >> .env
   echo "VERBOSE=false" >> .env
   ```

3. **Install dependencies using uv**:
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install project dependencies
   uv sync
   ```

4. **Run the application**:
   ```bash
   # Run with uv
   uv run main.py
   
   # Or with verbose logging for debugging
   VERBOSE=true uv run main.py
   ```

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Agent MCP Platform                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐                       │
│  │   User Input    │    │  Interactive    │                       │
│  │  (Terminal UI)  │◄──►│  CLI Handler    │                       │
│  └─────────────────┘    └─────────────────┘                       │
│           │                       │                                │
│           ▼                       ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                Agent Router                                 │   │
│  │  ┌─────────────────┐    ┌─────────────────────────────────┐ │   │
│  │  │ Job Finder      │    │ Bootcamp Agent                 │ │   │
│  │  │ Agent           │    │ + Guardrails                   │ │   │
│  │  │ (OpenAI GPT-4o) │    │ (OpenAI GPT-4o)                │ │   │
│  │  └─────────────────┘    └─────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│           │                       │                                │
│           ▼                       ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                MCP Layer                                    │   │
│  │  ┌─────────────────┐    ┌─────────────────────────────────┐ │   │
│  │  │ Firecrawl MCP   │    │ Bootcamp MCP                   │ │   │
│  │  │ Server          │    │ Server                         │ │   │
│  │  │ (Web Scraping)  │    │ (Knowledge Base)               │ │   │
│  │  └─────────────────┘    └─────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│           │                       │                                │
│           ▼                       ▼                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              External Services                              │   │
│  │  ┌─────────────────┐    ┌─────────────────────────────────┐ │   │
│  │  │ Hacker News     │    │ Agent Engineering               │ │   │
│  │  │ Jobs Page       │    │ Bootcamp Content                │ │   │
│  │  │ (HN/jobs)       │    │ (Vercel App)                    │ │   │
│  │  └─────────────────┘    └─────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Flow:
1. User selects agent via interactive menu
2. Agent processes user query using OpenAI GPT-4o
3. Agent calls appropriate MCP server for external data
4. MCP server fetches data from external services
5. Results stream back through Rich terminal interface
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `FIRECRAWL_API_KEY`: Your Firecrawl API key for web scraping (required)
- `VERBOSE`: Set to "true" for detailed logging (optional, defaults to false)

## How It Works

### Job Finder Agent
1. User describes the type of job they're looking for
2. Agent scrapes the Hacker News jobs page using Firecrawl MCP
3. Analyzes content to find the best matching job
4. Scrapes specific job pages for detailed information
5. Presents results in a clear, formatted manner

### Bootcamp Agent
1. User asks questions about agent engineering
2. Agent queries the bootcamp knowledge base via MCP
3. Guardrails check response relevance to bootcamp topics
4. Filtered, relevant responses are presented to the user

## Project Structure

```
├── main.py              # Main entry point with interactive CLI
├── agent.py             # Job Finder Agent implementation
├── bootcamp_agent.py    # Bootcamp Teaching Assistant
├── agent_guardrails.py  # Output guardrails for content filtering
├── mcp_config.py        # MCP server configuration and connections
├── logging_utils.py     # Rich console output and streaming utilities
├── pyproject.toml       # Project dependencies and configuration
└── .env                 # Environment variables (create this file)
```

## Terminal Features

### Clickable Links
URLs in the output will be clickable in supported terminals:
- **macOS**: iTerm2, Hyper, Kitty, WezTerm
- **Windows**: Windows Terminal, ConEmu
- **Linux**: GNOME Terminal (3.26+), Konsole, Tilix
- **Cross-platform**: VS Code integrated terminal, JetBrains IDEs terminal

### Rich Interface
- Interactive arrow-key navigation
- Real-time streaming responses
- Colored output with progress indicators
- Tool call visibility in verbose mode

## Dependencies

- `openai-agents`: OpenAI Agents SDK for AI agent functionality
- `python-dotenv`: Environment variable management
- `rich`: Enhanced terminal output and UI components
- `asyncio`: Asynchronous programming support (built-in)

## Troubleshooting

1. **Missing API Keys**: Ensure both OpenAI and Firecrawl API keys are set in `.env`
2. **Connection Issues**: Check your internet connection and API key validity
3. **Terminal Issues**: Use a supported terminal for the best experience
4. **Verbose Mode**: Set `VERBOSE=true` to see detailed operation logs