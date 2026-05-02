from __future__ import annotations

from enum import Enum
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


class StrategicGoal(BaseModel):
    name: str
    description: str
    target_metric: str
    target_value: float
    status: Status = Status.DRAFT


class Hypothesis(BaseModel):
    statement: str
    expected_outcome: str
    metric: str


class Experiment(BaseModel):
    name: str
    hypothesis: Hypothesis
    execution_plan: list[str]
    metrics: list[str]
    status: Status = Status.DRAFT


class Strategy(BaseModel):
    name: str
    goal: StrategicGoal
    experiments: list[Experiment] = Field(default_factory=list)
    execution_notes: list[str] = Field(default_factory=list)
    status: Status = Status.DRAFT


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
