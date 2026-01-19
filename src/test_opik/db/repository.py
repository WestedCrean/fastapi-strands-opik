import polars as pl
from typing import Optional


class Repository:
    def __init__(self):
        self.df = pl.read_delta("./data/processed_data.delta")

    def get_columns(self):
        return self.df.columns

    async def get_schema(self) -> dict[str, str]:
        """Get schema information (column names and types)."""
        return {col: str(dtype) for col, dtype in zip(self.df.columns, self.df.dtypes)}

    async def query_data(
        self,
        columns: Optional[list[str]] = None,
        filter_expr: Optional[str] = None,
        group_by: Optional[list[str]] = None,
        aggregations: Optional[dict[str, str]] = None,
        order_by: Optional[str] = None,
        order_descending: bool = True,
        limit: int = 40,
    ) -> dict:
        """Query data with various operations.

        Args:
            columns: List of columns to select. If None, select all.
            filter_expr: Polars filter expression as string (e.g., "pl.col('age') > 30")
            group_by: List of columns to group by
            aggregations: Dict mapping column names to aggregation functions
                         (e.g., {"revenue": "sum", "age": "mean"})
            order_by: Column name to order by
            order_descending: Whether to order descending (default True)
            limit: Maximum number of rows to return (default 40)

        Returns:
            Dictionary with 'data' (list of dicts) and 'shape' (rows, cols)
        """
        df = self.df

        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1

        # Apply filter
        if filter_expr:
            df = df.filter(eval(filter_expr))

        # Apply groupby and aggregations
        if group_by and aggregations:
            agg_exprs = []
            for col, agg_func in aggregations.items():
                if agg_func == "sum":
                    agg_exprs.append(pl.col(col).sum().alias(f"{col}_sum"))
                elif agg_func == "mean":
                    agg_exprs.append(pl.col(col).mean().alias(f"{col}_mean"))
                elif agg_func == "count":
                    agg_exprs.append(pl.col(col).count().alias(f"{col}_count"))
                elif agg_func == "min":
                    agg_exprs.append(pl.col(col).min().alias(f"{col}_min"))
                elif agg_func == "max":
                    agg_exprs.append(pl.col(col).max().alias(f"{col}_max"))
                elif agg_func == "std":
                    agg_exprs.append(pl.col(col).std().alias(f"{col}_std"))
                elif agg_func == "median":
                    agg_exprs.append(pl.col(col).median().alias(f"{col}_median"))

            df = df.group_by(group_by).agg(agg_exprs)

        # Select columns
        if columns:
            df = df.select(columns)

        # Order by
        if order_by:
            df = df.sort(order_by, descending=order_descending)

        # Apply limit
        df = df.limit(limit)

        # Convert to dict format
        result = {
            "data": df.to_dicts(),
            "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        }

        return result
