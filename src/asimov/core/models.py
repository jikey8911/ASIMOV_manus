from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Status(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class Opportunity(BaseModel):
    name: str
    market: str
    problem: str
    expected_value_usd_week: float
    risk_level: str = "medium"
    investment_level: str = "low"
    safety_score: float = 0.0
    viability_score: float = 0.0
    validation_notes: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class StrategicGoal(BaseModel):
    name: str
    description: str
    target_metric: str
    target_value: float
    status: Status = Status.DRAFT
    artifacts: dict[str, Any] = Field(default_factory=dict)


class Hypothesis(BaseModel):
    statement: str
    expected_outcome: str
    metric: str


class TacticalContext(BaseModel):
    identity_email: str
    openclaw_base_url: str
    openclaw_channel: str = "telegram"
    openclaw_available: bool = False
    ollama_base_url: str
    ollama_model: str = "qwen2.5:3b"
    ollama_available: bool = False
    frameworks: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    available_models: list[str] = Field(default_factory=list)


class Experiment(BaseModel):
    name: str
    hypothesis: Hypothesis
    execution_plan: list[str]
    metrics: list[str]
    status: Status = Status.DRAFT
    frameworks: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    artifacts: dict[str, Any] = Field(default_factory=dict)


class Strategy(BaseModel):
    name: str
    goal: StrategicGoal
    experiments: list[Experiment] = Field(default_factory=list)
    execution_notes: list[str] = Field(default_factory=list)
    status: Status = Status.DRAFT
    tooling: list[str] = Field(default_factory=list)
    execution_channel: str | None = None
    identity_email: str | None = None
    artifacts: dict[str, Any] = Field(default_factory=dict)


class ExecutionTask(BaseModel):
    name: str
    owner: str
    instructions: str
    status: Status = Status.DRAFT


class DigitalIdentity(BaseModel):
    """Representa la UAE de Credenciales para los Agentes."""

    email: str
    passwords: dict[str, str] = Field(default_factory=dict)
    session_cookies: dict[str, dict] = Field(default_factory=dict)
    api_keys: dict[str, str] = Field(default_factory=dict)
    active_sessions: list[str] = Field(default_factory=list)
