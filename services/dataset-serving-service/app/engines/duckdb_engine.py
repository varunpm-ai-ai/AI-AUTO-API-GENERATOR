"""
DuckDB Vectorized Analytical Engine Implementation.
Leverages in-process vectorized C++ execution with Parquet predicate pushdown and column pruning.
"""
from pathlib import Path
from typing import Dict, Any, Optional
import duckdb
import pyarrow as pa
import time
from app.engines.base import IAnalyticalEngine
from app.builders.query_builder import QuerySpecification
from app.security.ast_validator import ASTQueryValidator
from app.core.exceptions import QueryValidationError, QueryTimeoutError
from app.config.settings import settings
from app.config.logger import get_logger

logger = get_logger(__name__)


class DuckDBAnalyticalEngine(IAnalyticalEngine):
    """Executes high-speed analytical queries over Parquet datasets using DuckDB."""

    def __init__(self):
        self.max_memory = f"{settings.DUCKDB_MAX_MEMORY_MB}MB"
        self.threads = settings.DUCKDB_THREADS

    def _get_connection(self) -> duckdb.DuckDBPyConnection:
        """Creates an isolated in-memory DuckDB connection with sandboxed limits."""
        con = duckdb.connect(database=":memory:")
        con.execute(f"SET max_memory='{self.max_memory}'")
        con.execute(f"SET threads={self.threads}")
        con.execute("SET preserve_insertion_order=false")
        return con

    @staticmethod
    def _format_parquet_path(parquet_path: str) -> str:
        """Formats the parquet path with forward slashes for DuckDB read_parquet."""
        return str(parquet_path).replace("\\", "/")

    def execute_query(self, parquet_path: str, spec: QuerySpecification) -> pa.Table:
        """
        Executes query against the Parquet dataset using DuckDB.
        Pushes down column projections and row-group predicates.
        """
        clean_path = self._format_parquet_path(parquet_path)
        projection = spec.to_sql_projection()
        where_clause = spec.to_sql_where()
        order_clause = spec.to_sql_order_by()
        limit_clause = spec.to_sql_limit_offset()

        # Validate SQL fragments
        ASTQueryValidator.validate_sql(where_clause)
        ASTQueryValidator.validate_sql(order_clause)

        sql = f"SELECT {projection} FROM read_parquet('{clean_path}'){where_clause}{order_clause}{limit_clause}"
        logger.debug(f"Executing DuckDB SQL: {sql}")

        start_time = time.time()
        try:
            con = self._get_connection()
            result = con.sql(sql).to_arrow_table()
            duration_ms = (time.time() - start_time) * 1000.0

            if (time.time() - start_time) > settings.QUERY_TIMEOUT_SECONDS:
                raise QueryTimeoutError(f"Query exceeded analytical timeout limit of {settings.QUERY_TIMEOUT_SECONDS}s")

            logger.info(f"DuckDB query returned {len(result)} rows in {duration_ms:.2f}ms")
            return result

        except Exception as e:
            if isinstance(e, (QueryValidationError, QueryTimeoutError)):
                raise
            logger.error(f"DuckDB query execution failed: {e}", exc_info=True)
            raise QueryValidationError(f"Query execution error: {e}")

    def execute_count(self, parquet_path: str, spec: QuerySpecification) -> int:
        """Counts the total rows matching the WHERE criteria."""
        clean_path = self._format_parquet_path(parquet_path)
        where_clause = spec.to_sql_where()
        ASTQueryValidator.validate_sql(where_clause)

        sql = f"SELECT COUNT(*) as total FROM read_parquet('{clean_path}'){where_clause}"
        try:
            con = self._get_connection()
            rows = con.sql(sql).fetchall()
            return int(rows[0][0]) if rows and rows[0] else 0
        except Exception as e:
            logger.warning(f"Failed to execute count query: {e}")
            return 0

    def get_schema(self, parquet_path: str) -> pa.Schema:
        """Inspects Parquet file schema without reading data rows."""
        clean_path = self._format_parquet_path(parquet_path)
        sql = f"SELECT * FROM read_parquet('{clean_path}') LIMIT 0"
        con = self._get_connection()
        return con.sql(sql).to_arrow_table().schema

    def get_row_count(self, parquet_path: str) -> int:
        clean_path = self._format_parquet_path(parquet_path)
        sql = f"SELECT COUNT(*) FROM read_parquet('{clean_path}')"
        con = self._get_connection()
        rows = con.sql(sql).fetchall()
        return int(rows[0][0]) if rows and rows[0] else 0
