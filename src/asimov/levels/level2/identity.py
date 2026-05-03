from __future__ import annotations

import os
from typing import Any
from urllib.parse import urljoin

import requests

from asimov.core.models import DigitalIdentity, TacticalContext
from asimov.support.uaes import CredentialsUAE


class IdentityUAE:
    """UAE táctica para identidad, credenciales y acceso a OpenClaw/Ollama."""

    ENV_API_KEYS = {
        "openai": "OPENAI_API_KEY",
        "github": "GITHUB_TOKEN",
        "notion": "NOTION_API_KEY",
        "telegram": "TELEGRAM_BOT_TOKEN",
        "gemini": "GEMINI_API_KEY",
        "voyage": "VOYAGE_API_KEY",
    }

    def __init__(self, email: str | None = None) -> None:
        assigned_email = email or os.environ.get("ASIMOV_AGENT_EMAIL", "agent@asimov.local")
        self.identity = DigitalIdentity(email=assigned_email)
        self.openclaw_base_url = os.environ.get("OPENCLAW_BASE_URL", "http://100.115.61.47:18789")
        self.openclaw_api_key = os.environ.get("OPENCLAW_API_KEY") or os.environ.get("OPENCLAW_AUTH_TOKEN", "")
        self.openclaw_channel = os.environ.get("OPENCLAW_CHANNEL", "telegram")
        self.ollama_base_url = os.environ.get("ASIMOV_OLLAMA_URL") or os.environ.get("OLLAMA_HOST", "http://172.18.0.2:11434")
        self.ollama_model = os.environ.get("ASIMOV_OLLAMA_MODEL", "qwen2.5:3b")
        self.session = requests.Session()
        if self.openclaw_api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.openclaw_api_key}"})
        self._bootstrap_env_credentials()

    def _bootstrap_env_credentials(self) -> None:
        for service, env_name in self.ENV_API_KEYS.items():
            value = os.environ.get(env_name)
            if value:
                self.identity.api_keys[service] = value
        if self.openclaw_api_key:
            self.identity.api_keys["openclaw"] = self.openclaw_api_key

    def _health_get(self, url: str) -> bool:
        try:
            response = self.session.get(url, timeout=2)
            return response.ok
        except requests.RequestException:
            return False

    def openclaw_health(self) -> bool:
        return self._health_get(urljoin(f"{self.openclaw_base_url}/", "healthz"))

    def ollama_health(self) -> bool:
        return self._health_get(urljoin(f"{self.ollama_base_url}/", "api/tags"))

    def register_api_key(self, service: str, secret: str) -> None:
        self.identity.api_keys[service] = secret

    def register_password(self, service: str, password: str) -> None:
        self.identity.passwords[service] = password

    def register_session_cookie(self, service: str, cookies: dict[str, Any]) -> None:
        self.identity.session_cookies[service] = cookies
        if service not in self.identity.active_sessions:
            self.identity.active_sessions.append(service)

    def build_context(self) -> TacticalContext:
        capabilities = [
            "credential_storage",
            "browser_automation",
            "telegram_channel",
        ]
        if self.ollama_base_url:
            capabilities.append("local_llm")
        return TacticalContext(
            identity_email=self.identity.email,
            openclaw_base_url=self.openclaw_base_url,
            openclaw_channel=self.openclaw_channel,
            openclaw_available=self.openclaw_health(),
            ollama_base_url=self.ollama_base_url,
            ollama_model=self.ollama_model,
            ollama_available=self.ollama_health(),
            frameworks=["langgraph", "crew_ai", "skyvern"],
            capabilities=capabilities,
            available_models=[self.ollama_model],
        )

    def credentials_snapshot(self) -> dict[str, object]:
        registry = CredentialsUAE(
            identity_email=self.identity.email,
            openclaw_configured=bool(self.openclaw_api_key),
        )
        registry.register_service("openclaw", "Hub de skills, canales y automatizacion remota")
        registry.register_service("ollama", "Modelo local de apoyo tactico")
        for service in sorted(self.identity.api_keys):
            registry.register_api_key(service)
            if service not in registry.services:
                registry.register_service(service, f"Servicio autenticado por API key: {service}")
        for service in sorted(self.identity.passwords):
            registry.register_password(service)
            if service not in registry.services:
                registry.register_service(service, f"Servicio autenticado por credencial: {service}")
        for service in sorted(self.identity.session_cookies):
            registry.register_session(service)
            if service not in registry.services:
                registry.register_service(service, f"Servicio con sesion activa: {service}")
        snapshot = registry.snapshot()
        snapshot["openclaw_base_url"] = self.openclaw_base_url
        snapshot["openclaw_channel"] = self.openclaw_channel
        snapshot["ollama_base_url"] = self.ollama_base_url
        snapshot["ollama_model"] = self.ollama_model
        snapshot["health"] = {
            "openclaw": self.openclaw_health(),
            "ollama": self.ollama_health(),
        }
        return snapshot

    def execute_openclaw_skill(self, skill_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = urljoin(f"{self.openclaw_base_url}/", "api/v1/skills/execute")
        data = {
            "skill": skill_name,
            "payload": payload,
            "context": {"agent_email": self.identity.email},
        }
        try:
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            return {"error": str(exc), "skill": skill_name}

    def store_credential_in_openclaw(self, service: str, password: str) -> dict[str, Any]:
        self.register_password(service, password)
        return self.execute_openclaw_skill(
            "store_credential",
            {"service": service, "password": password},
        )

    def use_credential_for_login(self, service: str, login_url: str) -> dict[str, Any] | None:
        password = self.identity.passwords.get(service)
        if not password:
            return None
        return self.execute_openclaw_skill(
            "browser_login",
            {
                "url": login_url,
                "username": self.identity.email,
                "password": password,
            },
        )
