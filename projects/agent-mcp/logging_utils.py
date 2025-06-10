from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
import re


class LoggingUtils:
    def __init__(self, verbose: bool = False):
        self.console = Console()
        self.verbose = verbose

    def print_welcome(self, agent_name: str = None):
        self.console.print(Panel.fit(
            "[bold cyan]🚀 Agent Playground[/bold cyan]\n"
            "Powered by OpenAI Agents SDK & MCP Servers",
            border_style="cyan"
        ))

        if agent_name:
            self.console.print(Panel.fit(
                f"[bold cyan]You're talking to: {agent_name}[/bold cyan]\n"
                "I'm ready to help you with your request!",
                border_style="cyan"
            ))
        else:
            self.console.print(Panel.fit(
                "[bold cyan]Agent Assistant[/bold cyan]\n"
                "I'm ready to help you with your request!",
                border_style="cyan"
            ))

    def print_searching(self, agent_name: str = None):
        if agent_name:
            self.console.print(
                f"\n[bold yellow]🔍 {agent_name} is processing your request...[/bold yellow]\n")
        else:
            self.console.print(
                "\n[bold yellow]🔍 Processing your request...[/bold yellow]\n")

    def print_complete(self):
        self.console.print("\n" + "─" * self.console.width)
        self.console.print(Panel.fit(
            "[bold green]Task Complete![/bold green]",
            border_style="green"
        ))

    def print_connecting(self):
        if self.verbose:
            self.console.print(
                "\n[cyan]Connecting to MCP servers...[/cyan]")

    def print_connected(self):
        if self.verbose:
            self.console.print("[green]✓ Connected to MCP servers[/green]\n")

    async def stream_results(self, result):
        current_output = ""
        final_output = ""
        in_tool_call = False

        live_console = Console()

        with Live(console=live_console, refresh_per_second=4, transient=False) as live:
            async for event in result.stream_events():
                if event.type == "raw_response_event":
                    if hasattr(event, 'data') and hasattr(event.data, 'delta'):
                        delta = event.data.delta

                        if '{"url":' in delta or '"formats":' in delta or '"onlyMainContent":' in delta:
                            continue

                        current_output += delta
                        final_output += delta

                        try:
                            processed_output = self._make_links_clickable(
                                current_output)
                            live.update(Markdown(processed_output))
                        except:
                            live.update(current_output)

                elif event.type == "run_item_stream_event":
                    if hasattr(event, 'item'):
                        if event.item.type == "tool_call_item":
                            current_output = ""
                            in_tool_call = True

                            if self.verbose:
                                live.stop()

                                tool_name = (
                                    getattr(event.item, 'name', None) or
                                    getattr(event.item, 'tool_name', None) or
                                    getattr(event.item, 'function', {}).get('name', 'unknown') if hasattr(
                                        event.item, 'function') else 'unknown'
                                )
                                self.console.print(
                                    f"\n[bold blue]🔧 Calling tool:[/bold blue] [cyan]{tool_name}[/cyan]")
                                if hasattr(event.item, 'arguments'):
                                    args_str = str(event.item.arguments)
                                    if len(args_str) > 100:
                                        args_str = args_str[:100] + "..."
                                    self.console.print(
                                        f"[dim]   Arguments: {args_str}[/dim]")

                                live.start()

                        elif event.item.type == "tool_call_output_item":
                            in_tool_call = False
                            if self.verbose:
                                live.stop()
                                self.console.print(
                                    "[bold green]✅ Tool result received[/bold green]\n")
                                live.start()

                elif event.type == "agent_updated_stream_event":
                    if hasattr(event, 'new_agent') and self.verbose:
                        live.stop()
                        self.console.print(
                            f"\n[bold magenta]💬 Agent switched to:[/bold magenta] [cyan]{event.new_agent.name}[/cyan]")
                        live.start()

        self.console.print("\n" + "─" * self.console.width)
        try:
            processed_final = self._make_links_clickable(final_output)
            self.console.print(Markdown(processed_final))
        except:
            self.console.print(final_output)

    def _make_links_clickable(self, text: str) -> str:
        """Convert URLs in text to clickable links for terminals that support it"""
        url_pattern = r'(https?://[^\s<>"{}|\\^\[\]`]+)'

        def replace_url(match):
            url = match.group(1)
            return f"[{url}]({url})"

        return re.sub(url_pattern, replace_url, text)

    def print_with_links(self, text: str):
        """Print text with clickable links using Rich's native hyperlink support"""
        url_pattern = r'(https?://[^\s<>"{}|\\^\[\]`]+)'

        parts = re.split(url_pattern, text)
        rich_text = Text()

        for i, part in enumerate(parts):
            if i % 2 == 0:
                rich_text.append(part)
            else:
                rich_text.append(part, style=f"link {part}")

        self.console.print(rich_text)
