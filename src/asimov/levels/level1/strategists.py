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


class MarketAnalystAgent:
    """Busca oportunidades reales en internet, prioriza baja inversion y descarta fraude."""

    search_queries = (
        "low investment automation business opportunities",
        "zero investment online service business automation",
        "b2b automation opportunities small business workflow",
        "freelance proposal automation lead generation business",
    )

    def scan(self) -> list[Opportunity]:
        results: list[SearchResult] = []
        for query in self.search_queries:
            results.extend(self._search(query))

        curated = self._rank_templates(results)
        if curated:
            return curated
        return self._fallback()

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
        for item in channel.findall('item')[:12]:
            title = self._clean_html(item.findtext('title', default=''))
            snippet = self._clean_html(item.findtext('description', default=''))
            url = item.findtext('link', default='')
            if not title or self._looks_fraudulent(f"{title} {snippet}"):
                continue
            parsed.append(SearchResult(title=title, snippet=snippet, url=url))
        return parsed

    def _clean_html(self, value: str) -> str:
        value = re.sub(r"<.*?>", " ", value)
        value = unescape(value)
        return re.sub(r"\s+", " ", value).strip()

    def _looks_fraudulent(self, text: str) -> bool:
        normalized = text.lower()
        return any(keyword in normalized for keyword in FRAUD_KEYWORDS)

    def _rank_templates(self, results: list[SearchResult]) -> list[Opportunity]:
        ranked: list[tuple[float, Opportunity]] = []
        for template in OPPORTUNITY_TEMPLATES:
            score, notes, sources = self._score_template(template, results)
            if score < 2.5:
                continue
            safety_score = min(1.0, score / 6.0)
            risk_level = "low" if safety_score >= 0.75 else "medium"
            ranked.append(
                (
                    score,
                    Opportunity(
                        name=template.name,
                        market=template.market,
                        problem=template.problem,
                        expected_value_usd_week=template.expected_value_usd_week,
                        risk_level=risk_level,
                        investment_level=template.investment_level,
                        safety_score=round(safety_score, 2),
                        viability_score=round(min(1.0, score / 5.0), 2),
                        validation_notes=notes,
                        sources=sources,
                    ),
                )
            )
        ranked.sort(key=lambda item: (item[0], item[1].expected_value_usd_week), reverse=True)
        return [opportunity for _, opportunity in ranked[:3]]

    def _score_template(self, template: OpportunityTemplate, results: list[SearchResult]) -> tuple[float, list[str], list[str]]:
        score = 0.0
        notes: list[str] = []
        sources: list[str] = []
        for result in results:
            haystack = f"{result.title} {result.snippet}".lower()
            keyword_hits = sum(1 for keyword in template.keyword_groups if keyword in haystack)
            if not keyword_hits:
                continue
            score += 1.5 + (0.35 * keyword_hits)
            if any(keyword in haystack for keyword in LOW_INVESTMENT_KEYWORDS):
                score += 0.6
            if any(keyword in haystack for keyword in SAFE_KEYWORDS):
                score += 0.4
            if any(keyword in haystack for keyword in HIGH_INVESTMENT_KEYWORDS):
                score -= 0.8
            sources.append(result.url)
        if template.investment_level == "zero":
            score += 0.5
            notes.append("Priorizada por inversion inicial cero o casi nula.")
        else:
            notes.append("Seleccionada por inversion baja y posibilidad de vender como servicio.")
        notes.append("Resultados de internet filtrados para descartar patrones tipicos de fraude o promesas irreales.")
        if sources:
            notes.append(f"Validada con {len(sources)} hallazgos relevantes en busqueda abierta.")
        return score, notes, sources[:5]

    def _fallback(self) -> list[Opportunity]:
        return [
            Opportunity(
                name="Automatizacion de propuestas freelance",
                market="freelance",
                problem="Respuesta lenta a nuevas oportunidades",
                expected_value_usd_week=1200,
                risk_level="medium",
                investment_level="zero",
                safety_score=0.6,
                viability_score=0.6,
                validation_notes=[
                    "Fallback local activado por falta de resultados de busqueda.",
                    "La oportunidad conserva perfil de inversion cero o muy baja.",
                ],
            )
        ]


class StrategicPlanningAgent:
    """Convierte oportunidades filtradas en objetivos concretos sin depender de un LLM."""

    def define_goal(self, opportunity: Opportunity) -> StrategicGoal:
        target_value = max(1000.0, opportunity.expected_value_usd_week)
        return StrategicGoal(
            name=f"Capitalizar {opportunity.name}",
            description=(
                f"Construir una oferta automatizada segura y de {opportunity.investment_level} inversion para resolver: "
                f"{opportunity.problem}"
            ),
            target_metric="weekly_revenue_usd",
            target_value=target_value,
            artifacts={
                "market": opportunity.market,
                "risk_level": opportunity.risk_level,
                "investment_level": opportunity.investment_level,
                "safety_score": opportunity.safety_score,
                "viability_score": opportunity.viability_score,
                "sources": list(opportunity.sources),
                "validation_notes": list(opportunity.validation_notes),
            },
        )


class EthicsAndRiskAgent:
    """Aprueba solo objetivos seguros, realistas y coherentes con baja inversion."""

    def approve(self, goal: StrategicGoal) -> bool:
        artifacts = goal.artifacts
        safety_score = float(artifacts.get("safety_score", 0.0))
        viability_score = float(artifacts.get("viability_score", 0.0))
        investment_level = str(artifacts.get("investment_level", "low"))
        risk_level = str(artifacts.get("risk_level", "medium"))
        approved = (
            goal.target_value >= 1000.0
            and safety_score >= 0.45
            and viability_score >= 0.45
            and investment_level in {"zero", "low"}
            and risk_level != "high"
        )
        reason = (
            f"approved={approved}; safety_score={safety_score}; viability_score={viability_score}; "
            f"investment_level={investment_level}; risk_level={risk_level}"
        )
        print(f"EthicsAndRiskAgent Decision: {reason}")
        return approved
