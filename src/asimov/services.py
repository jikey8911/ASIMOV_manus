from __future__ import annotations

from typing import Any

import asyncpg
import httpx
from redis.asyncio import from_url as redis_from_url

from asimov.config import DependencyState, settings


class InfrastructureServices:
    def __init__(self) -> None:
        self.redis = None
        self.postgres_pool = None
        self.startup_errors: dict[str, str] = {}

    async def startup(self) -> None:
        if settings.redis_url:
            self.redis = redis_from_url(settings.redis_url, decode_responses=True)
        if settings.postgres_dsn:
            try:
                self.postgres_pool = await asyncpg.create_pool(
                    dsn=settings.postgres_dsn,
                    min_size=1,
                    max_size=3,
                )
            except Exception as exc:
                self.startup_errors["postgres"] = str(exc)
                self.postgres_pool = None

    async def shutdown(self) -> None:
        if self.redis is not None:
            await self.redis.aclose()
            self.redis = None
        if self.postgres_pool is not None:
            await self.postgres_pool.close()
            self.postgres_pool = None

    async def health(self) -> dict[str, dict[str, Any]]:
        return {
            "redis": (await self._check_redis()).model_dump(),
            "postgres": (await self._check_postgres()).model_dump(),
            "ollama": (await self._check_ollama()).model_dump(),
        }

    async def _check_redis(self) -> DependencyState:
        if self.redis is None:
            return DependencyState(ok=False, detail="not_configured")
        try:
            pong = await self.redis.ping()
            return DependencyState(ok=bool(pong), detail="pong" if pong else "unexpected_response")
        except Exception as exc:
            return DependencyState(ok=False, detail=str(exc))

    async def _check_postgres(self) -> DependencyState:
        if "postgres" in self.startup_errors:
            return DependencyState(ok=False, detail=self.startup_errors["postgres"])
        if self.postgres_pool is None:
            return DependencyState(ok=False, detail="not_configured")
        try:
            async with self.postgres_pool.acquire() as connection:
                value = await connection.fetchval("SELECT 1")
            return DependencyState(ok=value == 1, detail=f"query_result={value}")
        except Exception as exc:
            return DependencyState(ok=False, detail=str(exc))

    async def _check_ollama(self) -> DependencyState:
        if not settings.ollama_url:
            return DependencyState(ok=False, detail="not_configured")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.ollama_url}/api/tags")
            return DependencyState(
                ok=response.status_code == 200,
                detail=f"http_{response.status_code}",
            )
        except Exception as exc:
            return DependencyState(ok=False, detail=str(exc))
