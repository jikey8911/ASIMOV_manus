from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from pydantic import BaseModel

from asimov.config import settings
from asimov.runtime import RuntimeState
from asimov.services import InfrastructureServices


class RootResponse(BaseModel):
    message: str
    environment: str


class HealthResponse(BaseModel):
    status: str
    dependencies: dict[str, dict[str, Any]]


class SystemStatusResponse(BaseModel):
    app: str
    environment: str
    system: dict[str, Any]


@asynccontextmanager
async def lifespan(app: FastAPI):
    services = InfrastructureServices()
    runtime = RuntimeState()
    await services.startup()
    app.state.services = services
    app.state.runtime = runtime
    try:
        yield
    finally:
        await services.shutdown()


app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/", response_model=RootResponse)
async def read_root() -> RootResponse:
    return RootResponse(
        message="ASIMOV Backend is running",
        environment=settings.environment,
    )


@app.get("/health", response_model=HealthResponse)
async def health_check(request: Request) -> HealthResponse:
    dependencies = await request.app.state.services.health()
    status = "ok" if all(item["ok"] for item in dependencies.values()) else "degraded"
    return HealthResponse(status=status, dependencies=dependencies)


@app.get("/api/v1/system/status", response_model=SystemStatusResponse)
async def system_status(request: Request) -> SystemStatusResponse:
    runtime: RuntimeState = request.app.state.runtime
    return SystemStatusResponse(
        app=settings.app_name,
        environment=settings.environment,
        system=runtime.system_status(),
    )


@app.post("/api/v1/system/run")
async def run_cycle(request: Request) -> dict[str, Any]:
    runtime: RuntimeState = request.app.state.runtime
    return {
        "message": "ASIMOV orchestration cycle executed",
        "result": runtime.run_cycle(),
    }
