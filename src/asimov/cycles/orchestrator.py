from __future__ import annotations

from dataclasses import dataclass

from asimov.levels.level1.strategists import (
    EthicsAndRiskAgent,
    MarketAnalystAgent,
    StrategicPlanningAgent,
)
from asimov.levels.level2.scientific_cycle import TacticalUAE
from asimov.levels.level3.executors import (
    DataCollectionAgent,
    IntegrationAgent,
    ProcessExecutionAgent,
    QualityControlAgent,
)
from asimov.support.uaes import BrokerUAE, UserUAE


@dataclass(slots=True)
class OrchestrationResult:
    opportunity_name: str
    goal_name: str
    strategy_name: str
    tactical_identity_email: str
    tactical_channel: str
    tactical_tooling: list[str]
    executed_tasks: list[str]
    report: str


class AsimovOrchestrator:
    """Conecta los ciclos A y B de forma simplificada."""

    def __init__(self) -> None:
        self.market = MarketAnalystAgent()
        self.planner = StrategicPlanningAgent()
        self.risk = EthicsAndRiskAgent()
        self.tactical = TacticalUAE()
        self.integration = IntegrationAgent()
        self.data = DataCollectionAgent()
        self.executor = ProcessExecutionAgent()
        self.quality = QualityControlAgent()
        self.broker = BrokerUAE()
        self.user = UserUAE()

    def run(self) -> OrchestrationResult:
        opportunity = self.market.scan()[0]
        goal = self.planner.define_goal(opportunity)
        if not self.risk.approve(goal):
            raise RuntimeError("Objetivo rechazado por riesgo o baja viabilidad.")

        self.broker.approve(200)
        strategy = self.tactical.build_strategy(goal)

        tasks = [
            self.integration.create_task(strategy),
            self.data.create_task(strategy),
        ]
        executed = [self.executor.execute(task) for task in tasks]
        if not all(self.quality.validate(task) for task in executed):
            raise RuntimeError("Fallo el control de calidad.")

        report = (
            f"Ciclo A genero la estrategia '{strategy.name}' y ciclo B completo {len(executed)} tareas. "
            f"Nivel 2 opera con {strategy.execution_channel} usando la identidad {strategy.identity_email}."
        )
        self.user.publish_status(report)
        return OrchestrationResult(
            opportunity_name=opportunity.name,
            goal_name=goal.name,
            strategy_name=strategy.name,
            tactical_identity_email=strategy.identity_email or "",
            tactical_channel=strategy.execution_channel or "",
            tactical_tooling=list(strategy.tooling),
            executed_tasks=[task.name for task in executed],
            report=report,
        )
