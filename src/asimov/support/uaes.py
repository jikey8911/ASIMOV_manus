from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class CredentialsUAE:
    services: dict[str, str] = field(default_factory=dict)
    password_services: list[str] = field(default_factory=list)
    api_key_services: list[str] = field(default_factory=list)
    session_services: list[str] = field(default_factory=list)
    backends: list[str] = field(default_factory=lambda: ["memory", "openclaw"])
    identity_email: str = "agent@asimov.local"
    openclaw_configured: bool = False

    def register_service(self, service: str, purpose: str) -> None:
        self.services[service] = purpose

    def register_password(self, service: str) -> None:
        if service not in self.password_services:
            self.password_services.append(service)

    def register_api_key(self, service: str) -> None:
        if service not in self.api_key_services:
            self.api_key_services.append(service)

    def register_session(self, service: str) -> None:
        if service not in self.session_services:
            self.session_services.append(service)

    def snapshot(self) -> dict[str, object]:
        return {
            "identity_email": self.identity_email,
            "openclaw_configured": self.openclaw_configured,
            "services": dict(self.services),
            "password_services": list(self.password_services),
            "api_key_services": list(self.api_key_services),
            "session_services": list(self.session_services),
            "backends": list(self.backends),
        }


@dataclass(slots=True)
class MarketingUAE:
    active_campaigns: list[str] = field(default_factory=list)

    def launch_campaign(self, name: str) -> None:
        self.active_campaigns.append(name)


@dataclass(slots=True)
class BrokerUAE:
    approved_budget_usd: float = 0.0

    def approve(self, amount: float) -> None:
        self.approved_budget_usd += amount


@dataclass(slots=True)
class UserUAE:
    last_report: str = "Sin reporte"

    def publish_status(self, content: str) -> None:
        self.last_report = content


@dataclass(slots=True)
class EvolutionUAE:
    tracked_topics: list[str] = field(default_factory=lambda: ["CI/CD", "LLMs", "automatizacion"])

    def add_topic(self, topic: str) -> None:
        if topic not in self.tracked_topics:
            self.tracked_topics.append(topic)
