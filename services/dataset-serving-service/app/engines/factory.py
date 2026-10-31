"""
Analytical Engine Factory (Factory Pattern).
Instantiates and provides the active analytical query engine.
"""
from typing import Optional
from app.engines.base import IAnalyticalEngine
from app.engines.duckdb_engine import DuckDBAnalyticalEngine


class AnalyticalEngineFactory:
    """Factory resolving the active analytical query engine."""

    _instance: Optional[IAnalyticalEngine] = None

    @classmethod
    def get_engine(cls) -> IAnalyticalEngine:
        if cls._instance is None:
            cls._instance = DuckDBAnalyticalEngine()
        return cls._instance
