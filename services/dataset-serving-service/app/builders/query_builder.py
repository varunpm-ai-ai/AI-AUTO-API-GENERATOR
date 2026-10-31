"""
Query Specification and Fluent Builder (Builder Pattern).
Constructs safe, validated, and normalized analytical query specifications.
"""
from typing import List, Dict, Any, Optional
import hashlib
import json
import base64
from app.schemas.query import QueryRequest, FilterCondition, FilterOperator, SortClause, SortDirection
from app.core.exceptions import QueryValidationError


class QuerySpecification:
    """Immutable specification of projection, filtering, sorting, and pagination constraints."""

    def __init__(
        self,
        dataset_id: str,
        version: str = "latest",
        columns: Optional[List[str]] = None,
        filters: Optional[List[FilterCondition]] = None,
        sort: Optional[List[SortClause]] = None,
        page: int = 1,
        page_size: int = 50,
        cursor: Optional[str] = None
    ):
        self.dataset_id = dataset_id
        self.version = version
        self.columns = columns or []
        self.filters = filters or []
        self.sort = sort or []
        self.page = max(1, page)
        self.page_size = max(1, min(page_size, 1000))
        self.cursor = cursor
        self.offset = (self.page - 1) * self.page_size

        # If cursor provided, decode offset
        if self.cursor:
            try:
                decoded = base64.b64decode(self.cursor.encode("utf-8")).decode("utf-8")
                self.offset = int(decoded)
            except Exception:
                pass

    @staticmethod
    def _quote_identifier(name: str) -> str:
        escaped = str(name).replace('"', '""')
        return f'"{escaped}"'

    def to_sql_projection(self) -> str:
        """Returns safe SELECT clause projection string."""
        if not self.columns:
            return "*"
        safe_cols = [self._quote_identifier(col) for col in self.columns]
        return ", ".join(safe_cols)

    def to_sql_where(self) -> str:
        """Translates FilterConditions into parameterized or sanitized WHERE expression."""
        if not self.filters:
            return ""

        clauses = []
        for f in self.filters:
            col = self._quote_identifier(f.column)
            op = f.operator
            val = f.value

            if op == FilterOperator.EQ:
                clauses.append(f"{col} = '{self._sanitize_val(val)}'" if isinstance(val, str) else f"{col} = {val}")
            elif op == FilterOperator.NEQ:
                clauses.append(f"{col} != '{self._sanitize_val(val)}'" if isinstance(val, str) else f"{col} != {val}")
            elif op == FilterOperator.GT:
                clauses.append(f"{col} > {val}")
            elif op == FilterOperator.GTE:
                clauses.append(f"{col} >= {val}")
            elif op == FilterOperator.LT:
                clauses.append(f"{col} < {val}")
            elif op == FilterOperator.LTE:
                clauses.append(f"{col} <= {val}")
            elif op == FilterOperator.IN and isinstance(val, list):
                formatted_vals = [f"'{self._sanitize_val(v)}'" if isinstance(v, str) else str(v) for v in val]
                clauses.append(f"{col} IN ({', '.join(formatted_vals)})")
            elif op == FilterOperator.CONTAINS or op == FilterOperator.LIKE:
                clauses.append(f"{col} ILIKE '%{self._sanitize_val(val)}%'")
            elif op == FilterOperator.IS_NULL:
                clauses.append(f"{col} IS NULL")
            elif op == FilterOperator.IS_NOT_NULL:
                clauses.append(f"{col} IS NOT NULL")

        return " WHERE " + " AND ".join(clauses) if clauses else ""

    def to_sql_order_by(self) -> str:
        """Translates sort clauses into ORDER BY expression."""
        if not self.sort:
            return ""
        clauses = [
            f"{self._quote_identifier(s.column)} {s.direction.value.upper()}"
            for s in self.sort
        ]
        return " ORDER BY " + ", ".join(clauses)

    def to_sql_limit_offset(self) -> str:
        """Returns LIMIT and OFFSET clause."""
        return f" LIMIT {self.page_size} OFFSET {self.offset}"

    def get_cache_key(self) -> str:
        """Computes a deterministic SHA-256 hash representing this exact query."""
        payload = {
            "dataset_id": self.dataset_id,
            "version": self.version,
            "columns": sorted(self.columns),
            "filters": [(f.column, f.operator.value, str(f.value)) for f in self.filters],
            "sort": [(s.column, s.direction.value) for s in self.sort],
            "page": self.page,
            "page_size": self.page_size,
            "offset": self.offset
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def generate_next_cursor(self, returned_rows: int) -> Optional[str]:
        """Generates an opaque next cursor if there are potentially more rows."""
        if returned_rows < self.page_size:
            return None
        next_offset = self.offset + returned_rows
        return base64.b64encode(str(next_offset).encode("utf-8")).decode("utf-8")

    @staticmethod
    def _sanitize_val(val: Any) -> str:
        return str(val).replace("'", "''")


class QuerySpecificationBuilder:
    """Fluent Builder for QuerySpecification."""

    def __init__(self, dataset_id: str, version: str = "latest"):
        self.dataset_id = dataset_id
        self.version = version
        self.columns: List[str] = []
        self.filters: List[FilterCondition] = []
        self.sort: List[SortClause] = []
        self.page: int = 1
        self.page_size: int = 50
        self.cursor: Optional[str] = None

    def select(self, columns: List[str]) -> "QuerySpecificationBuilder":
        self.columns = columns
        return self

    def where(self, column: str, op: FilterOperator = FilterOperator.EQ, value: Any = None) -> "QuerySpecificationBuilder":
        self.filters.append(FilterCondition(column=column, operator=op, value=value))
        return self

    def sort_by(self, column: str, direction: SortDirection = SortDirection.ASC) -> "QuerySpecificationBuilder":
        self.sort.append(SortClause(column=column, direction=direction))
        return self

    def paginate(self, page: int = 1, page_size: int = 50, cursor: Optional[str] = None) -> "QuerySpecificationBuilder":
        self.page = page
        self.page_size = page_size
        self.cursor = cursor
        return self

    def from_request(self, req: QueryRequest) -> "QuerySpecificationBuilder":
        if req.columns:
            self.columns = req.columns
        if req.filters:
            self.filters.extend(req.filters)
        if req.sort:
            self.sort.extend(req.sort)
        if req.page:
            self.page = req.page
        if req.page_size:
            self.page_size = req.page_size
        if req.cursor:
            self.cursor = req.cursor
        if req.version:
            self.version = req.version
        return self

    def build(self) -> QuerySpecification:
        return QuerySpecification(
            dataset_id=self.dataset_id,
            version=self.version,
            columns=self.columns,
            filters=self.filters,
            sort=self.sort,
            page=self.page,
            page_size=self.page_size,
            cursor=self.cursor
        )
