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

    @opik.track()
    async def run(self, user_query: str) -> str:
        """Run the orchestrator agent to answer a user query."""
        return await self.agent.invoke_async(user_query)

    @opik.track()
    async def stream_response(self, user_query: str):
        """Stream the response from the agent for a given user query."""
        agent_stream = self.agent.stream_async(user_query)

        try:
            async for event in agent_stream:
                if "data" in event:
                    yield event["data"]
                elif "current_tool_use" in event and event["current_tool_use"].get(
                    "name"
                ):
                    tool_name = event["current_tool_use"]["name"]
                    yield f"\n[Using tool: {tool_name}]\n"
        except Exception as e:
            yield f"Error: {str(e)}"
