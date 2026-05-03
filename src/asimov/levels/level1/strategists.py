from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from urllib.parse import quote
from xml.etree import ElementTree

import requests

from asimov.core.models import Opportunity, StrategicGoal

SEARCH_URL = "https://news.google.com/rss/search?q={query}"
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0 Safari/537.36"
    )
}

FRAUD_KEYWORDS = {
    "ponzi", "binary options", "guaranteed profit", "double your money", "crypto doubling",
    "mlm", "multi-level marketing", "get rich quick", "risk-free return", "100% passive income",
    "arbitraje magico", "signal group", "pump and dump", "casino", "betting"
}

HIGH_INVESTMENT_KEYWORDS = {
    "franchise", "warehouse", "inventory", "manufacturing", "vehicle fleet", "heavy equipment",
    "retail store", "commercial lease", "capital intensive"
}

LOW_INVESTMENT_KEYWORDS = {
    "freelance", "automation", "agency", "service", "saas", "no-code", "digital", "crm",
    "outreach", "proposal", "lead", "appointment", "document", "claims", "support", "assistant"
}

SAFE_KEYWORDS = {
    "b2b", "workflow", "operations", "back office", "customer support", "compliance",
    "proposal", "lead generation", "crm", "invoicing", "document processing", "appointment setting"
}


@dataclass(slots=True)
class SearchResult:
    title: str
    snippet: str
    url: str


@dataclass(slots=True)
class OpportunityTemplate:
    name: str
    market: str
    problem: str
    expected_value_usd_week: float
    keyword_groups: tuple[str, ...]
    investment_level: str = "low"


OPPORTUNITY_TEMPLATES = [
    OpportunityTemplate(
        name="Automatizacion de propuestas freelance",
        market="freelance",
        problem="Respuesta lenta y manual a nuevas oportunidades comerciales.",
        expected_value_usd_week=1200,
        keyword_groups=("freelance", "proposal", "bid", "upwork", "lead", "outreach"),
        investment_level="zero",
    ),
    OpportunityTemplate(
        name="Calificacion automatizada de leads para pymes",
        market="lead_generation",
        problem="Pymes pierden oportunidades por no responder ni priorizar leads a tiempo.",
        expected_value_usd_week=1500,
        keyword_groups=("lead generation", "qualification", "crm", "sales", "appointment", "inbound"),
        investment_level="low",
    ),
    OpportunityTemplate(
        name="Automatizacion documental para seguros y reclamos",
        market="insurance_ops",
        problem="Procesos manuales en reclamos y validacion documental consumen tiempo operativo.",
        expected_value_usd_week=1800,
        keyword_groups=("insurance", "claims", "document processing", "intake", "verification"),
        investment_level="low",
    ),
    OpportunityTemplate(
        name="Asistente de soporte y seguimiento para ecommerce pequeno",
        market="ecommerce_support",
        problem="Tiendas pequenas no pueden responder rapido soporte, pedidos y postventa.",
        expected_value_usd_week=1300,
        keyword_groups=("ecommerce", "support", "order", "customer service", "chatbot"),
        investment_level="low",
    ),
    OpportunityTemplate(
        name="Automatizacion de agenda y recordatorios para negocios locales",
        market="local_services",
        problem="Negocios locales pierden reservas por seguimiento manual deficiente.",
        expected_value_usd_week=1100,
        keyword_groups=("appointment", "booking", "local business", "reminder", "whatsapp"),
        investment_level="zero",
    ),
]


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from asimov.config import settings

class MarketAnalystAgent:
    """Busca oportunidades reales en internet, prioriza baja inversion y descarta fraude."""

    search_queries = (
        "low investment automation business opportunities",
        "zero investment online service business automation",
        "b2b automation opportunities small business workflow",
        "freelance proposal automation lead generation business",
    )

    def __init__(self, llm: ChatGoogleGenerativeAI | None = None) -> None:
        self.llm = llm or ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.gemini_api_key,
            temperature=0.2
        )

    def scan(self) -> list[Opportunity]:
        results: list[SearchResult] = []
        for query in self.search_queries:
            results.extend(self._search(query))

        if not results:
            return self._fallback()

        # Usamos el LLM para filtrar y rankear las mejores oportunidades de los resultados reales
        return self._analyze_results_with_llm(results)

    def _search(self, query: str) -> list[SearchResult]:
        url = SEARCH_URL.format(query=quote(query))
        try:
            response = requests.get(url, headers=REQUEST_HEADERS, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            return []
        return self._parse_search_results(response.text)

    def _parse_search_results(self, xml_payload: str) -> list[SearchResult]:
        try:
            root = ElementTree.fromstring(xml_payload)
        except ElementTree.ParseError:
            return []
        parsed: list[SearchResult] = []
        channel = root.find('channel')
        if channel is None:
            return []
        for item in channel.findall('item')[:15]:
            title = self._clean_html(item.findtext('title', default=''))
            snippet = self._clean_html(item.findtext('description', default=''))
            url = item.findtext('link', default='')
            if not title:
                continue
            parsed.append(SearchResult(title=title, snippet=snippet, url=url))
        return parsed

    def _clean_html(self, value: str) -> str:
        value = re.sub(r"<.*?>", " ", value)
        value = unescape(value)
        return re.sub(r"\s+", " ", value).strip()

    def _analyze_results_with_llm(self, results: list[SearchResult]) -> list[Opportunity]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un Analista de Mercado experto en automatización y negocios de baja inversión. Tu tarea es analizar resultados de búsqueda reales y extraer las 3 mejores oportunidades de negocio que sean reales, de baja inversión (low/zero investment) y NO sean fraude (Ponzi, multinivel, etc.)."),
            ("user", "Resultados de búsqueda: {results}\n\nExtrae 3 oportunidades en formato JSON compatible con el modelo Opportunity.")
        ])
        
        # Definimos un extractor estructurado
        class OpportunityList(BaseModel):
            opportunities: list[Opportunity]

        structured_llm = self.llm.with_structured_output(OpportunityList)
        chain = prompt | structured_llm
        
        results_text = "\n".join([f"- {r.title}: {r.snippet} (Source: {r.url})" for r in results])
        try:
            output = chain.invoke({"results": results_text})
            return output.opportunities
        except Exception:
            return self._fallback()

    def _fallback(self) -> list[Opportunity]:
        return [
            Opportunity(
                name="Automatización de propuestas freelance",
                market="freelance",
                problem="Respuesta lenta a nuevas oportunidades",
                expected_value_usd_week=1200,
                risk_level="low",
                investment_level="zero",
                safety_score=0.9,
                viability_score=0.8,
                validation_notes=["Fallback activado por falta de resultados externos."],
            )
        ]


class StrategicPlanningAgent:
    """Convierte oportunidades en objetivos concretos usando LLM."""

    def __init__(self, llm: ChatGoogleGenerativeAI | None = None) -> None:
        self.llm = llm or ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.gemini_api_key,
            temperature=0.7
        )

    def define_goal(self, opportunity: Opportunity) -> StrategicGoal:
        structured_llm = self.llm.with_structured_output(StrategicGoal)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un Director de Estrategia de ASIMOV. Define un objetivo estratégico claro basado en una oportunidad detectada."),
            ("user", "Oportunidad: {opportunity}\n\nDefine el objetivo estratégico.")
        ])
        chain = prompt | structured_llm
        goal = chain.invoke({"opportunity": opportunity.model_dump()})
        return goal


class EthicsAndRiskAgent:
    """Aprueba o rechaza objetivos basados en análisis ético y de riesgo con LLM."""

    def __init__(self, llm: ChatGoogleGenerativeAI | None = None) -> None:
        self.llm = llm or ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.gemini_api_key,
            temperature=0.1
        )

    def approve(self, goal: StrategicGoal) -> bool:
        class Decision(BaseModel):
            approved: bool
            reason: str

        structured_llm = self.llm.with_structured_output(Decision)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un Auditor de Ética y Riesgo de ASIMOV. Tu misión es asegurar que los objetivos sean éticos, legales, de bajo riesgo y alta viabilidad. Rechaza cualquier cosa que parezca fraude, esquema Ponzi o sea demasiado arriesgada."),
            ("user", "Objetivo Estratégico: {goal}\n\n¿Es este objetivo seguro y viable? Responde con aprobación y motivo.")
        ])
        chain = prompt | structured_llm
        decision = chain.invoke({"goal": goal.model_dump()})
        print(f"EthicsAndRiskAgent Decision: {decision.reason}")
        return decision.approved

