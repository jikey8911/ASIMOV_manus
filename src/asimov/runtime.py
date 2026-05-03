from __future__ import annotations

from dataclasses import asdict

from asimov.cycles.orchestrator import AsimovOrchestrator
from asimov.support.uaes import CredentialsUAE, EvolutionUAE, MarketingUAE


class RuntimeState:
    def __init__(self) -> None:
        self.orchestrator = AsimovOrchestrator()
        self.credentials = self._build_credentials_uae()
        self.marketing = MarketingUAE()
        self.evolution = EvolutionUAE()
        self.last_result = None

    def _build_credentials_uae(self) -> CredentialsUAE:
        identity = self.orchestrator.tactical.identity
        snapshot = identity.credentials_snapshot()
        credentials = CredentialsUAE(
            services=dict(snapshot.get("services", {})),
            password_services=list(snapshot.get("password_services", [])),
            api_key_services=list(snapshot.get("api_key_services", [])),
            session_services=list(snapshot.get("session_services", [])),
            backends=list(snapshot.get("backends", [])),
            identity_email=str(snapshot.get("identity_email", "agent@asimov.local")),
            openclaw_configured=bool(snapshot.get("openclaw_configured", False)),
        )
        return credentials

    def run_cycle(self) -> dict[str, object]:
        self.credentials = self._build_credentials_uae()
        result = self.orchestrator.run()
        self.last_result = result
        return asdict(result)

    def system_status(self) -> dict[str, object]:
        self.credentials = self._build_credentials_uae()
        broker = self.orchestrator.broker
        user = self.orchestrator.user
        identity_snapshot = self.orchestrator.tactical.identity.credentials_snapshot()
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
                "level2": self.orchestrator.tactical.system_status(),
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
                "credentials": {
                    **self.credentials.snapshot(),
                    "identity": identity_snapshot,
                },
                "marketing": {"active_campaigns": list(self.marketing.active_campaigns)},
                "broker": {"approved_budget_usd": broker.approved_budget_usd},
                "user": {"last_report": user.last_report},
                "evolution": {"tracked_topics": list(self.evolution.tracked_topics)},
            },
            "last_result": asdict(self.last_result) if self.last_result else None,
        }
