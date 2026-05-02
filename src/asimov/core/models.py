from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Status(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class Opportunity:
    name: str
    market: str
    problem: str
    expected_value_usd_week: float
    risk_level: str = "medium"


@dataclass(slots=True)
class StrategicGoal:
    name: str
    description: str
    target_metric: str
    target_value: float
    status: Status = Status.DRAFT


@dataclass(slots=True)
class Hypothesis:
    statement: str
    expected_outcome: str
    metric: str


@dataclass(slots=True)
class Experiment:
    name: str
    hypothesis: Hypothesis
    execution_plan: list[str]
    metrics: list[str]
    status: Status = Status.DRAFT


@dataclass(slots=True)
class Strategy:
    name: str
    goal: StrategicGoal
    experiments: list[Experiment] = field(default_factory=list)
    execution_notes: list[str] = field(default_factory=list)
    status: Status = Status.DRAFT


@dataclass(slots=True)
class ExecutionTask:
    name: str
    owner: str
    instructions: str
    status: Status = Status.DRAFT
