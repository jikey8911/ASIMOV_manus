from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class CredentialsUAE:
    services: dict[str, str] = field(default_factory=dict)

    def register_service(self, service: str, purpose: str) -> None:
        self.services[service] = purpose


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
