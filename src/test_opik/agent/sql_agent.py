import os
import json
from typing import Any, Literal, Optional
import polars as pl
import opik
from strands import Agent, tool
from strands.models.anthropic import AnthropicModel

from test_opik.db.repository import Repository
from test_opik.agent import BaseAgent

import logging

logger = logging.getLogger("sql_agent")
logger.setLevel(logging.DEBUG)


class SQLAgent(BaseAgent):
    def __init__(self, repository: Repository, model: AnthropicModel):
        super().__init__(name="SQL Agent", model=model)
        self.repository = repository

        # Create tools
        @tool(
            name="get_schema",
            description="Get the schema of the dataset including all column names and their data types. Use this first to understand what data is available.",
        )
        @opik.track(
            name="get_schema",
            tags=["tool", "sql_agent"],
        )
        async def get_schema() -> dict[str, str]:
            """Get schema information showing all columns and their types."""
            return await self.repository.get_schema()

        @tool(
            name="query_data",
            description=(
                "Query the dataset with various operations including: selecting columns, filtering rows, "
                "grouping and aggregating data, ordering results, and limiting output. "
                "By default returns up to 40 results in descending order. "
                "Supports aggregations: sum, mean, count, min, max, std, median. "
                "Filter expressions use Polars syntax: pl.col('column_name') > 5, pl.col('name') == 'John', etc."
            ),
        )
        @opik.track(
            name="query_data",
            tags=["tool", "sql_agent"],
        )
        async def query_data(
            columns: Optional[list[str]] = None,
            filter_expr: Optional[str] = None,
            group_by: Optional[list[str]] = None,
            aggregations: Optional[dict[str, str]] = None,
            order_by: Optional[str] = None,
            order_descending: bool = True,
            limit: int = 40,
        ) -> dict:
            """Query data from the dataset.

            Args:
                columns: List of specific columns to select. If None, selects all columns.
                filter_expr: Polars filter expression as string (e.g., "pl.col('age') > 30")
                group_by: List of columns to group by for aggregations
                aggregations: Dict mapping column names to aggregation functions
                             (e.g., {"revenue": "sum", "age": "mean"})
                             Available: sum, mean, count, min, max, std, median
                order_by: Column name to sort results by
                order_descending: Whether to sort in descending order (default True)
                limit: Maximum number of rows to return (default 40)

            Returns:
                Dictionary containing 'data' (list of row dictionaries) and 'shape' (rows and columns count)
            """
            return await self.repository.query_data(
                columns=columns,
                filter_expr=filter_expr,
                group_by=group_by,
                aggregations=aggregations,
                order_by=order_by,
                order_descending=order_descending,
                limit=limit,
            )

        self.tools = [get_schema, query_data]

        # Create agent
        self.agent = Agent(
            model=model,
            tools=self.tools,
            system_prompt=(
                "You are a SQL analysis agent. You have access to a dataset and can query it using the available tools. "
                "When using filter expressions, use Polars syntax (e.g., pl.col('column_name') > 5). "
                "Always start by getting the schema to understand the available columns. "
                "Provide clear, concise answers based on the data."
            ),
        )
