import os
import json
from typing import Any
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel
from strands.models.gemini import GeminiModel
from strands.models.mistral import MistralModel

from test_opik.agent import BaseAgent, SQLAgent
from test_opik.db.repository import Repository
from test_opik.agent.hooks import LimitSQLAgentCalls
import logging

logger = logging.getLogger("orchestrator_agent")
logger.setLevel(logging.DEBUG)


class OrchestratorAgent(BaseAgent):
    def __init__(self, sql_agent: SQLAgent, model: AnthropicModel):
        super().__init__(name="OrchestratorAgent", model=model)
        self.sql_agent = sql_agent
        self.model = model

        # Create tools
        @tool(
            name="query_sql_agent",
            description=(
                "Query the SQL agent to retrieve and analyze data. The SQL agent has access to the dataset "
                "and can perform various operations including: getting schema information, selecting specific columns, "
                "filtering data, performing aggregations (sum, mean, count, min, max, std, median), "
                "grouping data, ordering results (default descending), and limiting output (default 40 rows). "
                "Use this tool whenever you need to retrieve or analyze data from the dataset."
            ),
        )
        async def query_sql_agent(query: str) -> str:
            """Query the SQL agent with a natural language question about the data.

            Args:
                query: Natural language question or instruction for the SQL agent
                      (e.g., "What are the top 10 products by revenue?",
                       "Show me the average age by country", etc.)

            Returns:
                The SQL agent's response with the requested data and analysis
            """
            res = await self.sql_agent.run(query)

            logger.debug(f"SQL Agent response: {res}")
            return res

        self.tools = [query_sql_agent]

        # Create agent
        self.agent = Agent(
            model=model,
            tools=self.tools,
            system_prompt=(
                "You are an analyst orchestrator agent. Your role is to help users analyze data by coordinating with a SQL agent. "
                "You can ask the SQL agent to query data, perform aggregations, and provide insights. "
                "Break down complex questions into simpler queries if needed. "
                "Provide clear, insightful answers based on the data retrieved from the SQL agent. "
                "If the user asks for data analysis, always use the SQL agent to retrieve the data."
                "Try to minimize the number of calls to the SQL agent and keep each response short and concise."
            ),
            hooks=[LimitSQLAgentCalls(max_calls=self.recursion_limit)],
        )


async def get_orchestrator_agent() -> OrchestratorAgent:
    """Create and return an orchestrator agent with all dependencies."""
    model_provider = "mistral"
    if model_provider == "mistral":
        model = MistralModel(
            client_args={
                "api_key": os.environ.get("MISTRAL_API_KEY"),
            },
            max_tokens=1028,
            model_id="ministral-8b-latest",
            params={
                "temperature": 0.7,
            },
        )
    elif model_provider == "anthropic":
        model = AnthropicModel(
            client_args={
                "api_key": os.environ.get("ANTHROPIC_API_KEY"),
            },
            max_tokens=1028,
            model_id="claude-haiku-4-5-20251001",
            params={
                "temperature": 0.7,
            },
        )
    else:
        model = GeminiModel(
            client_args={
                "api_key": os.environ.get("GOOGLE_API_KEY"),
            },
            model_id="gemini-2.5-flash",
            params={
                "temperature": 0.7,
            },
        )
    repository = Repository()
    sql_agent = SQLAgent(repository, model)
    return OrchestratorAgent(sql_agent, model)
