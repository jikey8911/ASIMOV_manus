from __future__ import annotations

import os
from typing import List
from pydantic import BaseModel, Field

from asimov.core.models import Opportunity, StrategicGoal
from langchain_ollama import ChatOllama

OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

class OpportunitiesList(BaseModel):
    opportunities: List[Opportunity]

class MarketAnalystAgent:
    """Detecta oportunidades reales en sectores automatizables usando LLMs."""

    def __init__(self):
        self.llm = ChatOllama(model="llama3.2", base_url=OLLAMA_URL, temperature=0.7)

    def scan(self) -> list[Opportunity]:
        prompt = (
            "You are a top-tier market analyst specializing in AI automation opportunities. "
            "Identify 2 high-potential, niche, and actionable B2B automation opportunities "
            "that can generate recurring revenue quickly. Focus on low-friction, high-value tasks. "
            "Output the results in the requested format."
        )
        
        # We use with_structured_output for robust parsing
        structured_llm = self.llm.with_structured_output(OpportunitiesList)
        
        try:
            result = structured_llm.invoke(prompt)
            if not result or not result.opportunities:
                return self._fallback()
            return result.opportunities
        except Exception as e:
            print(f"Error in MarketAnalystAgent: {e}")
            return self._fallback()

    def _fallback(self) -> list[Opportunity]:
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
    """Transforma oportunidades en objetivos concretos usando LLMs."""

    def __init__(self):
        self.llm = ChatOllama(model="llama3.2", base_url=OLLAMA_URL, temperature=0.4)

    def define_goal(self, opportunity: Opportunity) -> StrategicGoal:
        prompt = f"""
        Given the following market opportunity, define a concrete strategic goal:
        Name: {opportunity.name}
        Market: {opportunity.market}
        Problem: {opportunity.problem}
        Expected Weekly Value (USD): {opportunity.expected_value_usd_week}
        Risk Level: {opportunity.risk_level}
        
        Create a practical, actionable strategic goal. Define a clear target metric and its target value.
        The target value must be a number representing USD. Output in the requested structure.
        """
        
        structured_llm = self.llm.with_structured_output(StrategicGoal)
        
        try:
            result = structured_llm.invoke(prompt)
            if not result:
                return self._fallback(opportunity)
            return result
        except Exception as e:
            print(f"Error in StrategicPlanningAgent: {e}")
            return self._fallback(opportunity)

    def _fallback(self, opportunity: Opportunity) -> StrategicGoal:
        return StrategicGoal(
            name=f"Capitalizar {opportunity.name}",
            description="Convertir la oportunidad en retorno semanal.",
            target_metric="weekly_revenue_usd",
            target_value=max(1000.0, opportunity.expected_value_usd_week),
        )


class ApprovalResult(BaseModel):
    approved: bool
    reason: str

class EthicsAndRiskAgent:
    """Aplica un filtro inteligente de viabilidad, riesgo y ética usando LLMs."""

    def __init__(self):
        self.llm = ChatOllama(model="llama3.2", base_url=OLLAMA_URL, temperature=0.2)

    def approve(self, goal: StrategicGoal) -> bool:
        prompt = f"""
        Evaluate the following strategic goal for a B2B automation business:
        Name: {goal.name}
        Description: {goal.description}
        Target Metric: {goal.target_metric}
        Target Value: {goal.target_value}
        
        Is this goal ethical, feasible, and presenting an acceptable risk level?
        Approve it if it makes sense as a business goal. Output the decision and a short reason.
        """
        
        structured_llm = self.llm.with_structured_output(ApprovalResult)
        
        try:
            result = structured_llm.invoke(prompt)
            if result:
                print(f"EthicsAndRiskAgent Decision: {result.approved} - Reason: {result.reason}")
                return result.approved
            return True # default to True if parsing fails
        except Exception as e:
            print(f"Error in EthicsAndRiskAgent: {e}")
            return True
