import hashlib
import json
import time
import uuid
from typing import Callable, Dict, Optional

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class IdempotencyMiddleware(BaseHTTPMiddleware):
    """
    Middleware to ensure idempotency of API requests.

    This middleware checks for an idempotency key in the request headers and ensures
    that requests with the same key return the same response,
    even if called multiple times.

    The idempotency key is expected in the 'Idempotency-Key' header.

    Note: This middleware requires Redis for distributed locking and caching.
    """

    def __init__(
        self,
        app: ASGIApp,
        redis_client,
        header_name: str = "Idempotency-Key",
        expiration_time: int = 86400,  # 24 hours in seconds
        lock_timeout: int = 30,  # 30 seconds lock timeout
        exempt_paths: Optional[list] = None,
        exempt_methods: Optional[list] = None,
    ):
        """
        Initialize the idempotency middleware.

        Args:
            app: The ASGI application
            redis_client: Redis client for caching responses (required)
            header_name: The name of the header containing the idempotency key
            expiration_time: Time in seconds to keep idempotent requests in cache
            lock_timeout: Time in seconds before a lock expires (prevents deadlocks)
            exempt_paths: List of path prefixes to exempt from idempotency checks
            exempt_methods: List of HTTP methods to exempt from idempotency checks

        Raises:
            ValueError: If redis_client is None
        """
        super().__init__(app)

        if redis_client is None:
            raise ValueError("Redis client is required for IdempotencyMiddleware")

        self.redis_client = redis_client
        self.header_name = header_name
        self.expiration_time = expiration_time
        self.lock_timeout = lock_timeout
        self.exempt_paths = exempt_paths or ["/health", "/docs", "/openapi.json"]
        self.exempt_methods = exempt_methods or ["GET", "HEAD", "OPTIONS"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request through the middleware.

        Args:
            request: The incoming request
            call_next: Function to call the next middleware or route handler

        Returns:
            The response from the route handler or a cached response
        """
        # Skip idempotency check for exempt paths and methods
        if self._should_skip_idempotency_check(request):
            return await call_next(request)

        # Get idempotency key from headers
        idempotency_key = request.headers.get(self.header_name)
        if not idempotency_key:
            return await call_next(request)

        # Create a unique cache key based on the idempotency key and request path
        cache_key = self._create_cache_key(idempotency_key, request)
        lock_key = f"{cache_key}:lock"

        # Generate a unique process identifier for this request instance
        process_id = str(uuid.uuid4())

        # First, check if we already have a cached response (fast path)
        cached_response = await self._get_cached_response(cache_key)
        if cached_response:
            return Response(
                content=cached_response["body"],
                status_code=cached_response["status_code"],
                headers=cached_response["headers"],
                media_type=cached_response["media_type"],
            )

        # If no cached response, try to acquire a lock
        lock_acquired = await self._acquire_lock(lock_key, process_id)

        if not lock_acquired:
            raise HTTPException(
                status_code=409, detail="Request is already in progress"
            )

        try:
            return await call_next(request)
        except Exception as e:
            raise e
        finally:
            # Always release the lock if we acquired it
            if lock_acquired:
                await self._release_lock(lock_key, process_id)

    async def _acquire_lock(self, lock_key: str, process_id: str) -> bool:
        """
        Acquire a distributed lock to prevent race conditions.

        Args:
            lock_key: The key to use for the lock
            process_id: A unique identifier for this process

        Returns:
            True if the lock was acquired, False otherwise
        """
        # Try to set the key only if it doesn't exist (NX) with an expiration (EX)
        return await self.redis_client.set(
            lock_key, process_id, nx=True, ex=self.lock_timeout
        )

    async def _release_lock(self, lock_key: str, process_id: str) -> bool:
        """
        Release a previously acquired lock.

        Args:
            lock_key: The key used for the lock
            process_id: The unique identifier for this process

        Returns:
            True if the lock was released, False otherwise
        """
        # Only delete the key if it still contains our process_id
        # This prevents accidentally deleting a lock acquired by another process
        script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        return bool(await self.redis_client.eval(script, 1, lock_key, process_id))

    async def _sleep(self, seconds: float) -> None:
        """
        Sleep for the specified number of seconds.

        Args:
            seconds: The number of seconds to sleep
        """
        import asyncio

        await asyncio.sleep(seconds)

    def _should_skip_idempotency_check(self, request: Request) -> bool:
        """
        Determine if idempotency check should be skipped for this request.

        Args:
            request: The incoming request

        Returns:
            True if idempotency check should be skipped, False otherwise
        """
        # Skip for exempt HTTP methods
        if request.method in self.exempt_methods:
            return True

        # Skip for exempt paths
        for path in self.exempt_paths:
            if request.url.path.startswith(path):
                return True

        return False

    def _create_cache_key(self, idempotency_key: str, request: Request) -> str:
        """
        Create a unique cache key for the request.

        Args:
            idempotency_key: The idempotency key from the request header
            request: The incoming request

        Returns:
            A unique cache key string
        """
        # Use a hash of the idempotency key and path to create a unique key
        key_base = f"{idempotency_key}:{request.url.path}"
        return f"idempotency:{hashlib.md5(key_base.encode()).hexdigest()}"

    async def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """
        Get a cached response for the given cache key.

        Args:
            cache_key: The cache key to look up

        Returns:
            The cached response data or None if not found
        """
        cached_data = await self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        return None

    async def _cache_response(self, cache_key: str, response: Response) -> None:
        """
        Cache the response for future requests with the same idempotency key.

        Args:
            cache_key: The cache key to store the response under
            response: The response to cache
        """
        # Get response body
        response_body = response.body if hasattr(response, "body") else b""

        # Prepare data for caching
        cache_data = {
            "body": response_body,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "media_type": response.media_type,
            "timestamp": time.time(),
        }

        # Cache in Redis
        await self.redis_client.setex(
            cache_key,
            self.expiration_time,
            json.dumps(
                cache_data,
                default=lambda x: x.decode("utf-8") if isinstance(x, bytes) else str(x),
            ),
        )
