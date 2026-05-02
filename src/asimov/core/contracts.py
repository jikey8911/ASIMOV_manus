from __future__ import annotations

from typing import Protocol

from asimov.core.models import Experiment, ExecutionTask, Opportunity, Strategy, StrategicGoal


class OpportunitySource(Protocol):
    def scan(self) -> list[Opportunity]:
        """Retorna oportunidades detectadas por el nivel estratégico."""


class Strategist(Protocol):
    def define_goal(self, opportunity: Opportunity) -> StrategicGoal:
        """Convierte una oportunidad en un objetivo estratégico."""


class TacticalUnit(Protocol):
    def build_strategy(self, goal: StrategicGoal) -> Strategy:
        """Convierte un objetivo en una estrategia ejecutable."""


class Executor(Protocol):
    def execute(self, task: ExecutionTask) -> ExecutionTask:
        """Ejecuta una tarea operativa."""


class ExperimentSupervisor(Protocol):
    def evaluate(self, experiment: Experiment) -> Experiment:
        """Evalúa el resultado de un experimento."""
