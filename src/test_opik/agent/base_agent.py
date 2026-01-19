import os
import opik
from strands import Agent


class BaseAgent:
    """Base class for all agents, providing common functionality and tracing."""

    def __init__(
        self, name: str, model: str, description: str = None, recursion_limit: int = 3
    ):
        self.name: str = name
        self.model: str = model
        self.description: str = description
        self.agent: Agent = None
        self.recursion_limit: int = recursion_limit

    @opik.track(project_name=os.getenv("OPIK_PROJECT_NAME", "test-opik"))
    async def run(self, user_query: str) -> str:
        """Run the orchestrator agent to answer a user query."""
        return await self.agent.invoke_async(user_query)
