"""
Idempotency Guard.
Guarantees deduplicated at-most-once processing using Redis atomic locks with an in-memory fallback.
"""
from typing import Optional, Set
import redis
from app.config.settings import settings
from app.config.logger import get_logger

logger = get_logger(__name__)


class IdempotencyGuard:
    """Manages atomic locks and status tracking for preprocessing job IDs."""

    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.ttl = settings.IDEMPOTENCY_TTL_SECONDS
        self._redis_client: Optional[redis.Redis] = None
        self._memory_cache: Set[str] = set()

    @property
    def redis(self) -> Optional[redis.Redis]:
        if self._redis_client is None:
            try:
                client = redis.from_url(self.redis_url, decode_responses=True)
                client.ping()
                self._redis_client = client
            except Exception as e:
                logger.warning(f"Redis unavailable ({e}). Using in-memory idempotency guard fallback.")
                self._redis_client = None
        return self._redis_client

    def acquire_lock(self, job_id: str) -> bool:
        """
        Attempts to acquire an exclusive lock for the given job_id.
        Returns True if acquired (job can run), False if already processed or processing.
        """
        key = f"job:idempotency:{job_id}"
        if self.redis:
            try:
                # Set if Not eXists with expiration TTL
                acquired = bool(self.redis.set(key, "PROCESSING", nx=True, ex=self.ttl))
                return acquired
            except Exception as e:
                logger.warning(f"Redis error during acquire_lock: {e}")

        # In-memory fallback
        if job_id in self._memory_cache:
            return False
        self._memory_cache.add(job_id)
        return True

    def mark_completed(self, job_id: str) -> None:
        """Marks the job as completed."""
        key = f"job:idempotency:{job_id}"
        if self.redis:
            try:
                self.redis.set(key, "COMPLETED", ex=self.ttl)
            except Exception as e:
                logger.warning(f"Redis error during mark_completed: {e}")

    def release_lock(self, job_id: str) -> None:
        """Releases the lock upon job failure or cancellation to allow retries."""
        key = f"job:idempotency:{job_id}"
        if self.redis:
            try:
                self.redis.delete(key)
            except Exception:
                pass
        self._memory_cache.discard(job_id)


idempotency_guard = IdempotencyGuard()
