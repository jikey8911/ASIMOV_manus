from __future__ import annotations

from asimov.core.models import Experiment, Hypothesis, Status, Strategy, StrategicGoal


class HypothesisAgent:
    def create(self, goal: StrategicGoal) -> Hypothesis:
        return Hypothesis(
            statement=(
                "Si automatizamos la deteccion y respuesta a oportunidades, "
                "el ingreso semanal aumentara de forma consistente."
            ),
            expected_outcome="Mayor tasa de conversion de oportunidades a contratos.",
            metric=goal.target_metric,
        )


class ExperimentalDesignAgent:
    def design(self, goal: StrategicGoal, hypothesis: Hypothesis) -> Experiment:
        return Experiment(
            name=f"Experimento para {goal.name}",
            hypothesis=hypothesis,
            execution_plan=[
                "Escuchar nuevas ofertas o hacer polling periodico.",
                "Generar propuesta con contexto del servicio.",
                "Enviar propuesta y registrar respuesta.",
                "Medir conversion, costo y tiempo de cierre.",
            ],
            metrics=[
                "weekly_revenue_usd",
                "proposal_conversion_rate",
                "execution_time_minutes",
            ],
            status=Status.ACTIVE,
        )


class SupervisionAndAnalysisAgent:
    def evaluate(self, experiment: Experiment) -> Experiment:
        experiment.status = Status.COMPLETED
        return experiment


class SynthesisAgent:
    def build_strategy(self, goal: StrategicGoal, experiment: Experiment) -> Strategy:
        return Strategy(
            name=f"Estrategia derivada de {goal.name}",
            goal=goal,
            experiments=[experiment],
            execution_notes=[
                "Mantener el proceso en ejecucion continua.",
                "Retroalimentar resultados al ciclo tactico.",
            ],
            status=Status.ACTIVE,
        )


class TacticalUAE:
    """Unidad táctica que encapsula el ciclo científico."""

    def __init__(self) -> None:
        self.hypothesis_agent = HypothesisAgent()
        self.design_agent = ExperimentalDesignAgent()
        self.supervisor = SupervisionAndAnalysisAgent()
        self.synthesis = SynthesisAgent()

    def build_strategy(self, goal: StrategicGoal) -> Strategy:
        hypothesis = self.hypothesis_agent.create(goal)
        experiment = self.design_agent.design(goal, hypothesis)
        evaluated = self.supervisor.evaluate(experiment)
        return self.synthesis.build_strategy(goal, evaluated)
