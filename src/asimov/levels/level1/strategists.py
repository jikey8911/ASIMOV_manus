from __future__ import annotations

from asimov.core.models import Opportunity, StrategicGoal


class MarketAnalystAgent:
    """Detecta oportunidades iniciales en sectores automatizables."""

    def scan(self) -> list[Opportunity]:
        return [
            Opportunity(
                name="Automatizacion de propuestas freelance",
                market="freelance",
                problem="Respuesta lenta a nuevas oportunidades",
                expected_value_usd_week=1200,
                risk_level="medium",
            )
        ]


class StrategicPlanningAgent:
    """Transforma oportunidades en objetivos concretos."""

    def define_goal(self, opportunity: Opportunity) -> StrategicGoal:
        return StrategicGoal(
            name=f"Capitalizar {opportunity.name}",
            description=(
                "Convertir la oportunidad detectada en una linea operativa "
                "con retorno semanal medible."
            ),
            target_metric="weekly_revenue_usd",
            target_value=max(1000.0, opportunity.expected_value_usd_week),
        )


class EthicsAndRiskAgent:
    """Aplica un filtro simple de viabilidad y riesgo."""

    def approve(self, goal: StrategicGoal) -> bool:
        return goal.target_value >= 1000
