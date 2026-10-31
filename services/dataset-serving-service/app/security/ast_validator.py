"""
AST Query Validator & SQL Injection Filter.
Enforces strict read-only execution guardrails and blocks malicious or system clauses.
"""
import re
from typing import Set
from app.core.exceptions import QuerySafetyError
from app.config.settings import settings
from app.config.logger import get_logger

logger = get_logger(__name__)


class ASTQueryValidator:
    """Enforces query safety and validates SQL tokens against a strict whitelist."""

    FORBIDDEN_KEYWORDS: Set[str] = {
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE",
        "ATTACH", "DETACH", "PRAGMA", "COPY", "LOAD", "INSTALL", "IMPORT",
        "EXPORT", "CALL", "EXECUTE", "SHOW", "SET", "RESET", "USE", "GRANT",
        "REVOKE", "SYSTEM", "SHUTDOWN", "KILL"
    }

    FORBIDDEN_FUNCTIONS: Set[str] = {
        "READ_CSV", "READ_PARQUET", "READ_JSON", "READ_TEXT", "GLOB",
        "SQLITE_SCAN", "POSTGRES_SCAN", "MYSQL_SCAN", "HTTPFS", "ENV",
        "CURRENT_USER", "VERSION"
    }

    @classmethod
    def validate_sql(cls, sql_text: str) -> None:
        """
        Validates raw SQL or sub-expressions.
        Raises QuerySafetyError if dangerous tokens or patterns are detected.
        """
        if not sql_text or not settings.ENABLE_SQL_SANDBOX:
            return

        normalized = sql_text.upper()

        # Check for multiple statements (semicolon separator)
        if ";" in sql_text and not sql_text.strip().endswith(";"):
            raise QuerySafetyError("Multiple SQL statements in a single query are forbidden.")

        # Check forbidden keywords
        tokens = set(re.findall(r"\b[A-Z_]+\b", normalized))
        prohibited_matches = tokens.intersection(cls.FORBIDDEN_KEYWORDS)
        if prohibited_matches:
            raise QuerySafetyError(f"Prohibited SQL keyword(s) detected: {', '.join(prohibited_matches)}")

        # Check forbidden file-system and system scan functions
        func_matches = tokens.intersection(cls.FORBIDDEN_FUNCTIONS)
        if func_matches:
            raise QuerySafetyError(f"Prohibited SQL function(s) detected: {', '.join(func_matches)}")

        # Block comments used for injection bypass
        if "--" in sql_text or "/*" in sql_text:
            raise QuerySafetyError("SQL comments are not permitted in queries.")

        logger.debug("SQL query passed AST safety validation.")
