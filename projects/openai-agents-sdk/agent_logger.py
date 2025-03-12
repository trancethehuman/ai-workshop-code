import logging
from typing import Any, Optional

from agents import RunContextWrapper, RunHooks, Agent, Tool
from agent_context import AgentContext

# Configure module logger
logger = logging.getLogger("founder_agent")


class AgentLogger:
    """
    Agent logger configuration with ability to enable/disable logging.
    """

    # Class variable to control overall logging
    enabled = True

    @classmethod
    def configure(cls, enabled: bool = True, log_level: str = "INFO"):
        """
        Configure the logger settings

        Args:
            enabled: Whether to enable logging
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        cls.enabled = enabled

        # Set the log level based on the parameter
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {log_level}")

        logger.setLevel(numeric_level)

    @classmethod
    def log(cls, level: str, message: str):
        """
        Log a message if logging is enabled

        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Message to log
        """
        if not cls.enabled:
            return

        # Get the appropriate logging method
        log_method = getattr(logger, level.lower(), None)
        if log_method is None:
            raise ValueError(f"Invalid log level: {level}")

        log_method(message)

    @classmethod
    def info(cls, message: str):
        """Log an info message"""
        cls.log("info", message)

    @classmethod
    def warning(cls, message: str):
        """Log a warning message"""
        cls.log("warning", message)

    @classmethod
    def error(cls, message: str):
        """Log an error message"""
        cls.log("error", message)

    @classmethod
    def debug(cls, message: str):
        """Log a debug message"""
        cls.log("debug", message)


# Create lifecycle hooks with configurable logging
class AgentLifecycleLogger(RunHooks[AgentContext]):
    """
    Configurable lifecycle hooks that can be enabled or disabled
    """

    def __init__(self, enabled: bool = True):
        """
        Initialize the lifecycle logger

        Args:
            enabled: Whether to enable logging for this instance
        """
        super().__init__()
        self.enabled = enabled

    def _log_if_enabled(self, level: str, message: str):
        """Log only if both class and instance logging are enabled"""
        if self.enabled:
            AgentLogger.log(level, message)

    async def on_agent_start(
        self, context: RunContextWrapper[AgentContext], agent: Agent[AgentContext]
    ) -> None:
        self._log_if_enabled("info", f"🚀 Agent started: {agent.name}")
        self._log_if_enabled(
            "info",
            f"Context state: {len(context.context.recent_searches)} searches, "
            f"{len(context.context.recent_documents)} documents",
        )

    async def on_agent_end(
        self,
        context: RunContextWrapper[AgentContext],
        agent: Agent[AgentContext],
        output: Any,
    ) -> None:
        self._log_if_enabled(
            "info",
            f"✅ Agent {agent.name} finished with output length: {len(str(output))}",
        )
        self._log_if_enabled(
            "info",
            f"Final context state: {len(context.context.recent_searches)} searches, "
            f"{len(context.context.recent_documents)} documents",
        )

    async def on_handoff(
        self,
        context: RunContextWrapper[AgentContext],
        from_agent: Agent[AgentContext],
        to_agent: Agent[AgentContext],
    ) -> None:
        self._log_if_enabled(
            "info", f"🔄 Handoff from {from_agent.name} to {to_agent.name}"
        )

    async def on_tool_start(
        self,
        context: RunContextWrapper[AgentContext],
        agent: Agent[AgentContext],
        tool: Tool,
    ) -> None:
        self._log_if_enabled(
            "info", f"🔧 Tool started: {tool.name} by agent {agent.name}"
        )

    async def on_tool_end(
        self,
        context: RunContextWrapper[AgentContext],
        agent: Agent[AgentContext],
        tool: Tool,
        result: str,
    ) -> None:
        self._log_if_enabled(
            "info", f"🔧 Tool {tool.name} completed. Result length: {len(result)}"
        )


# Create a minimal logger that only logs final output
class MinimalLogger(AgentLifecycleLogger):
    """
    Minimal logger that only logs the final output
    """

    async def on_agent_end(
        self,
        context: RunContextWrapper[AgentContext],
        agent: Agent[AgentContext],
        output: Any,
    ) -> None:
        # We're only overriding this method to disable logging
        # of the final output, but still call hooks
        pass
