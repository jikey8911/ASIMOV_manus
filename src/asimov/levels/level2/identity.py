import os
import requests
from typing import Optional, Dict, Any
from asimov.core.models import DigitalIdentity

class IdentityUAE:
    """Unidad Autónoma de Ejecución (UAE) de Credenciales e Identidad.
    Se integra con el contenedor de OpenClaw para manejar cuentas, sesiones y apis usando sus Skills.
    """

    def __init__(self, email: Optional[str] = None):
        assigned_email = email or os.environ.get("ASIMOV_AGENT_EMAIL", "agent@asimov.local")
        self.identity = DigitalIdentity(email=assigned_email)
        self.openclaw_base_url = os.environ.get("OPENCLAW_BASE_URL", "http://openclaw_clean-openclaw-gateway-1:5000")
        self.openclaw_api_key = os.environ.get("OPENCLAW_API_KEY", "")
        self.headers = {"Authorization": f"Bearer {self.openclaw_api_key}"} if self.openclaw_api_key else {}

    def execute_openclaw_skill(self, skill_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta un skill dentro de OpenClaw para acceder a una cuenta o API."""
        url = f"{self.openclaw_base_url}/api/v1/skills/execute"
        data = {
            "skill": skill_name,
            "payload": payload,
            "context": {
                "agent_email": self.identity.email
            }
        }
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error executing OpenClaw skill '{skill_name}': {e}")
            return {"error": str(e)}

    def store_credential_in_openclaw(self, service: str, password: str):
        """Usa OpenClaw para guardar una credencial de forma segura (Vault/Credentials)."""
        # Guardamos localmente para referencia
        self.identity.passwords[service] = password
        # Guardamos en OpenClaw
        self.execute_openclaw_skill("store_credential", {"service": service, "password": password})

    def use_credential_for_login(self, service: str, login_url: str):
        """Ejecuta un skill de login automatizado en OpenClaw para la UAE."""
        password = self.identity.passwords.get(service)
        if not password:
            print(f"No password registered for {service}")
            return None
            
        print(f"[{self.identity.email}] Solicitando a OpenClaw el login en {service}...")
        return self.execute_openclaw_skill("browser_login", {
            "url": login_url,
            "username": self.identity.email,
            "password": password
        })
