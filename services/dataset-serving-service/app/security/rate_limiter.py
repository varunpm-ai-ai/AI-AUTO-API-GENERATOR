"""
Rate Limiter (Sliding Window & Token Bucket).
Protects the serving cluster from abusive query bursts using Redis with an in-memory fallback.
"""
import time
from typing import Optional, Dict
import redis
from app.config.settings import settings
from app.core.exceptions import RateLimitExceededError
from app.config.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Sliding-window rate limiter per client identifier."""

    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.max_requests = settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        self._redis_client: Optional[redis.Redis] = None
        self._memory_buckets: Dict[str, list] = {}

    @property
    def redis(self) -> Optional[redis.Redis]:
        if self._redis_client is None:
            try:
                client = redis.from_url(self.redis_url, decode_responses=True)
                client.ping()
                self._redis_client = client
            except Exception as e:
                logger.warning(f"Redis unavailable for rate limiting ({e}). Using in-memory fallback.")
                self._redis_client = None
        return self._redis_client

    def check_rate_limit(self, client_id: str) -> None:
        """
        Asserts that the client has not exceeded their request quota for the current minute window.
        Raises RateLimitExceededError if limit is breached.
        """
        now = time.time()
        window_seconds = 60
        key = f"rate_limit:{client_id}"

        # 1. Try Redis sliding window counter
        if self.redis:
            try:
                pipe = self.redis.pipeline()
                pipe.zremrangebyscore(key, 0, now - window_seconds)
                pipe.zadd(key, {str(now): now})
                pipe.zcard(key)
                pipe.expire(key, window_seconds + 5)
                results = pipe.execute()

                current_count = results[2]
                if current_count > self.max_requests:
                    logger.warning(f"Rate limit exceeded for client {client_id}: {current_count}/{self.max_requests}")
                    raise RateLimitExceededError(
                        f"Rate limit exceeded. Maximum {self.max_requests} requests per minute.",
                        details={"client_id": client_id, "limit": self.max_requests, "window": "60s"}
                    )
                return
            except Exception as e:
                if isinstance(e, RateLimitExceededError):
                    raise
                logger.warning(f"Redis rate limit check failed: {e}. Falling back to memory.")

        # 2. In-memory sliding window fallback
        timestamps = self._memory_buckets.get(client_id, [])
        # Prune expired timestamps
        timestamps = [ts for ts in timestamps if now - ts < window_seconds]
        if len(timestamps) >= self.max_requests:
            raise RateLimitExceededError(
                f"Rate limit exceeded. Maximum {self.max_requests} requests per minute.",
                details={"client_id": client_id, "limit": self.max_requests, "window": "60s"}
            )
        timestamps.append(now)
        self._memory_buckets[client_id] = timestamps


rate_limiter = RateLimiter()
