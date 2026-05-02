from __future__ import annotations

from dataclasses import asdict

from asimov.cycles.orchestrator import AsimovOrchestrator
from asimov.support.uaes import CredentialsUAE, EvolutionUAE, MarketingUAE


class RuntimeState:
    def __init__(self) -> None:
        self.orchestrator = AsimovOrchestrator()
        self.credentials = CredentialsUAE()
        self.marketing = MarketingUAE()
        self.evolution = EvolutionUAE()
        self.last_result = None

    def run_cycle(self) -> dict[str, object]:
        result = self.orchestrator.run()
        self.last_result = result
        return asdict(result)

    def system_status(self) -> dict[str, object]:
        broker = self.orchestrator.broker
        user = self.orchestrator.user
        return {
            "levels": {
                "level1": {
                    "name": "El Estratega",
                    "agents": [
                        "market_analyst_agent",
                        "strategic_planning_agent",
                        "ethics_and_risk_agent",
                    ],
                    "frameworks": ["langgraph"],
                    "status": "active",
                },
                "level2": {
                    "name": "El Tactico",
                    "agents": [
                        "hypothesis_agent",
                        "experimental_design_agent",
                        "supervision_and_analysis_agent",
                        "synthesis_agent",
                    ],
                    "frameworks": ["langgraph", "crew_ai", "skyvern"],
                    "status": "active",
                },
                "level3": {
                    "name": "El Ejecutor",
                    "agents": [
                        "integration_agent",
                        "data_collection_agent",
                        "process_execution_agent",
                        "quality_control_agent",
                    ],
                    "runtime": "ollama",
                    "status": "active",
                },
            },
            "cycles": {
                "cycle_a": {
                    "description": "Detecta oportunidades y genera estrategias.",
                    "status": "active",
                },
                "cycle_b": {
                    "description": "Ejecuta estrategias y realimenta optimizacion.",
                    "status": "active",
                },
            },
            "uaes": {
                "credentials": {"services": dict(self.credentials.services)},
                "marketing": {"active_campaigns": list(self.marketing.active_campaigns)},
                "broker": {"approved_budget_usd": broker.approved_budget_usd},
                "user": {"last_report": user.last_report},
                "evolution": {"tracked_topics": list(self.evolution.tracked_topics)},
            },
            "last_result": asdict(self.last_result) if self.last_result else None,
        }
