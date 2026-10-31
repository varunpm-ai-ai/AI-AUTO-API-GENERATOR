"""
Unit Tests for QuerySpecificationBuilder, AST Safety Validator, and Rate Limiter.
"""
import pytest
from app.builders.query_builder import QuerySpecificationBuilder
from app.schemas.query import FilterOperator, SortDirection
from app.security.ast_validator import ASTQueryValidator
from app.security.rate_limiter import RateLimiter
from app.core.exceptions import QuerySafetyError, RateLimitExceededError


def test_query_specification_builder():
    builder = QuerySpecificationBuilder("ds-123", version="v1")
    spec = (
        builder.select(["col_a", "col_b"])
        .where("col_a", FilterOperator.EQ, "test_val")
        .sort_by("col_b", SortDirection.ASC)
        .paginate(page=2, page_size=25)
        .build()
    )

    assert spec.to_sql_projection() == '"col_a", "col_b"'
    assert "WHERE \"col_a\" = 'test_val'" in spec.to_sql_where()
    assert 'ORDER BY "col_b" ASC' in spec.to_sql_order_by()
    assert "LIMIT 25 OFFSET 25" in spec.to_sql_limit_offset()
    assert len(spec.get_cache_key()) == 64


def test_ast_validator_blocks_malicious_clauses():
    # Dangerous statements must raise QuerySafetyError
    with pytest.raises(QuerySafetyError):
        ASTQueryValidator.validate_sql("DROP TABLE users;")

    with pytest.raises(QuerySafetyError):
        ASTQueryValidator.validate_sql("ATTACH 'database.db' AS db;")

    with pytest.raises(QuerySafetyError):
        ASTQueryValidator.validate_sql("SELECT * FROM read_csv('secret.csv')")

    with pytest.raises(QuerySafetyError):
        ASTQueryValidator.validate_sql("SELECT 1; DELETE FROM dataset")

    # Safe statements pass
    ASTQueryValidator.validate_sql("WHERE id > 10 AND department = 'IT'")


def test_rate_limiter_exceeded():
    limiter = RateLimiter()
    limiter.max_requests = 3
    client_id = "test-client-ip-123"

    # 3 requests pass
    limiter.check_rate_limit(client_id)
    limiter.check_rate_limit(client_id)
    limiter.check_rate_limit(client_id)

    # 4th request must raise RateLimitExceededError
    with pytest.raises(RateLimitExceededError):
        limiter.check_rate_limit(client_id)
