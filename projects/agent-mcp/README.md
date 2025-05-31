# Job Finder Agent

An AI-powered job finder that scrapes Hacker News jobs and finds positions matching your preferences.

## Project Structure

The project is organized into modular components:

```
├── main.py           # Main entry point
├── agent.py          # Job finder agent logic
├── mcp_config.py     # MCP server configuration
├── logging_utils.py  # Console output and logging utilities
└── .env             # Environment variables
```

### Files Overview

- **`main.py`**: The main entry point that orchestrates the application
- **`agent.py`**: Contains the `JobFinderAgent` class with the core job finding logic
- **`mcp_config.py`**: Contains the `MCPConfig` class for Firecrawl MCP server setup
- **`logging_utils.py`**: Contains the `LoggingUtils` class for all console output and streaming results

## Setup

1. Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your_openai_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
VERBOSE=false  # Set to true for detailed logging
```

2. Install dependencies (if not already installed):

```bash
pip install agents rich python-dotenv
```

3. Run the application:

```bash
python main.py
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `FIRECRAWL_API_KEY`: Your Firecrawl API key for web scraping
- `VERBOSE`: Set to "true" for detailed logging (optional, defaults to false)

## How It Works

1. The user is prompted to describe what kind of job they're looking for
2. The agent scrapes the Hacker News jobs page
3. It analyzes the content to find the best matching job
4. It scrapes the specific job page for more details
5. Finally, it presents the job information in a clear, concise manner

## Terminal Features

### Clickable Links

URLs in the output will be clickable in terminals that support hyperlinks:

- **macOS**: iTerm2, Hyper, Kitty, WezTerm
- **Windows**: Windows Terminal, ConEmu
- **Linux**: GNOME Terminal (3.26+), Konsole, Tilix
- **Cross-platform**: VS Code integrated terminal, JetBrains IDEs terminal

If your terminal doesn't support clickable links, URLs will still be highlighted and you can copy-paste them.
