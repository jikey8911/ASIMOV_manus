from __future__ import annotations

from asimov.core.models import ExecutionTask, Status, Strategy


class IntegrationAgent:
    def create_task(self, strategy: Strategy) -> ExecutionTask:
        return ExecutionTask(
            name=f"Integrar automatizacion para {strategy.name}",
            owner="integration_agent",
            instructions=(
                "Conectar APIs, persistencia y componentes necesarios para "
                "dejar la estrategia operativa."
            ),
            status=Status.ACTIVE,
        )


class DataCollectionAgent:
    def create_task(self, strategy: Strategy) -> ExecutionTask:
        return ExecutionTask(
            name=f"Recolectar datos para {strategy.name}",
            owner="data_collection_agent",
            instructions="Extraer señales, ofertas, eventos y metricas de operacion.",
            status=Status.ACTIVE,
        )


class ProcessExecutionAgent:
    def execute(self, task: ExecutionTask) -> ExecutionTask:
        task.status = Status.COMPLETED
        return task


class QualityControlAgent:
    def validate(self, task: ExecutionTask) -> bool:
        return task.status == Status.COMPLETED
