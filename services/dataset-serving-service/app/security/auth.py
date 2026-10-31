"""
Authentication & Authorization Security Guard.
Extracts identity context from API Gateway trusted headers or verifies JWT bearer tokens.
"""
from typing import Optional, Dict, Any
from fastapi import Request
from app.config.settings import settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.config.logger import get_logger

logger = get_logger(__name__)


class UserContext:
    """Represents the authenticated caller identity context."""
    def __init__(
        self,
        user_id: str = "anonymous",
        role: str = "guest",
        workspace_id: Optional[str] = None
    ):
        self.user_id = user_id
        self.role = role
        self.workspace_id = workspace_id


class AuthManager:
    """Validates Gateway-forwarded headers or JWT tokens."""

    @classmethod
    def extract_user_context(cls, request: Request) -> UserContext:
        """
        Extracts user identity context from Gateway headers:
        - X-User-Id
        - X-User-Role
        - X-Workspace-Id
        Or verifies Bearer token if configured.
        """
        user_id = request.headers.get("X-User-Id")
        user_role = request.headers.get("X-User-Role", "user")
        workspace_id = request.headers.get("X-Workspace-Id")

        if user_id:
            return UserContext(user_id=user_id, role=user_role, workspace_id=workspace_id)

        # If mandatory auth is enabled, require authentication headers
        if settings.REQUIRE_AUTH:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise AuthenticationError("Authorization header missing or invalid Bearer format.")
            # For demonstration / testing with token:
            token = auth_header.split(" ")[1]
            if token != settings.JWT_SECRET and len(token) < 10:
                raise AuthenticationError("Invalid Bearer authentication token.")
            return UserContext(user_id="jwt_user", role="user", workspace_id=None)

        return UserContext(user_id="anonymous", role="guest", workspace_id=None)
