from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from asimov.config import settings
from asimov.core.models import Experiment, Hypothesis, Status, Strategy, StrategicGoal, TacticalContext
from asimov.levels.level2.identity import IdentityUAE


class TacticalGraphState(TypedDict, total=False):
    goal: StrategicGoal
    context: TacticalContext
    hypothesis: Hypothesis
    experiment: Experiment
    strategy: Strategy
    readiness: Literal["connected", "partial"]
    plan_mode: Literal["remote_enabled", "local_first"]
    trace: list[str]
    runtime: dict[str, object]


class HypothesisAgent:
    def __init__(self, llm: ChatGoogleGenerativeAI) -> None:
        self.llm = llm.with_structured_output(Hypothesis)

    def create(self, goal: StrategicGoal, context: TacticalContext) -> Hypothesis:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un Estratega Científico de ASIMOV. Tu tarea es generar una hipótesis táctica basada en un objetivo estratégico y un contexto operativo."),
            ("user", "Objetivo: {goal}\nContexto: {context}\n\nGenera una hipótesis clara y medible.")
        ])
        chain = prompt | self.llm
        return chain.invoke({"goal": goal.model_dump(), "context": context.model_dump()})


class ExperimentalDesignAgent:
    def __init__(self, llm: ChatGoogleGenerativeAI) -> None:
        self.llm = llm.with_structured_output(Experiment)

    def design(
        self,
        goal: StrategicGoal,
        hypothesis: Hypothesis,
        context: TacticalContext,
        plan_mode: str,
    ) -> Experiment:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un Arquitecto de Experimentos de ASIMOV. Diseña un plan de ejecución táctico real usando las herramientas disponibles (OpenClaw, Ollama, LangGraph, CrewAI, Skyvern)."),
            ("user", "Objetivo: {goal}\nHipótesis: {hypothesis}\nContexto: {context}\nModo: {plan_mode}\n\nDiseña un experimento detallado.")
        ])
        chain = prompt | self.llm
        return chain.invoke({
            "goal": goal.model_dump(),
            "hypothesis": hypothesis.model_dump(),
            "context": context.model_dump(),
            "plan_mode": plan_mode
        })


class SupervisionAndAnalysisAgent:
    def __init__(self, llm: ChatGoogleGenerativeAI) -> None:
        self.llm = llm # Para análisis libre antes de retornar el objeto

    def evaluate(self, experiment: Experiment, context: TacticalContext) -> tuple[Experiment, str]:
        # Aquí podríamos hacer una evaluación más profunda con el LLM
        # Por ahora, mantenemos la lógica de readiness pero enriquecida por el LLM si fuera necesario
        readiness = "connected" if context.openclaw_available and context.ollama_available else "partial"
        experiment.artifacts["connectivity"] = {
            "openclaw": context.openclaw_available,
            "ollama": context.ollama_available,
        }
        experiment.artifacts["readiness"] = readiness
        experiment.status = Status.COMPLETED
        return experiment, readiness


class SynthesisAgent:
    def __init__(self, llm: ChatGoogleGenerativeAI) -> None:
        self.llm = llm.with_structured_output(Strategy)

    def build_strategy(
        self,
        goal: StrategicGoal,
        experiment: Experiment,
        context: TacticalContext,
        trace: list[str],
    ) -> Strategy:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres el Sintetizador Central de ASIMOV. Consolida el experimento y el contexto en una estrategia operativa final."),
            ("user", "Objetivo: {goal}\nExperimento: {experiment}\nContexto: {context}\nTraza: {trace}\n\nSintetiza la estrategia.")
        ])
        chain = prompt | self.llm
        strategy = chain.invoke({
            "goal": goal.model_dump(),
            "experiment": experiment.model_dump(),
            "context": context.model_dump(),
            "trace": trace
        })
        # Asegurar que el canal y la identidad se mantengan
        strategy.execution_channel = context.openclaw_channel
        strategy.identity_email = context.identity_email
        return strategy



class TacticalUAE:
    """Unidad táctica con ciclo científico orquestado por LangGraph."""

    def __init__(
        self,
        identity_uae: IdentityUAE | None = None,
        llm: ChatGoogleGenerativeAI | None = None,
    ) -> None:
        self.identity = identity_uae or IdentityUAE()
        self.llm = llm or ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.gemini_api_key,
            temperature=0.7
        )
        self.hypothesis_agent = HypothesisAgent(self.llm)

        self.design_agent = ExperimentalDesignAgent(self.llm)
        self.supervisor = SupervisionAndAnalysisAgent(self.llm)
        self.synthesis = SynthesisAgent(self.llm)
        self.last_context: TacticalContext | None = None
        self.last_strategy: Strategy | None = None
        self.last_trace: list[str] = []
        self.last_runtime: dict[str, object] = self._runtime_config()
        self.graph = self._build_graph()

    def _append_trace(self, state: TacticalGraphState, label: str) -> list[str]:
        trace = list(state.get("trace", []))
        trace.append(label)
        return trace

    def _runtime_config(self) -> dict[str, object]:
        tracing_enabled = bool(settings.langgraph_tracing_enabled and settings.langgraph_api_key)
        return {
            "engine": "langgraph",
            "api_key_configured": bool(settings.langgraph_api_key),
            "tracing_enabled": tracing_enabled,
            "project": settings.langgraph_project,
            "endpoint": settings.langgraph_endpoint,
            "checkpointing": False,
        }

    def _build_graph(self):
        graph = StateGraph(TacticalGraphState)
        graph.add_node("context", self._context_node)
        graph.add_node("hypothesis", self._hypothesis_node)
        graph.add_node("design_remote", self._design_remote_node)
        graph.add_node("design_local", self._design_local_node)
        graph.add_node("supervision", self._supervision_node)
        graph.add_node("synthesis", self._synthesis_node)
        graph.add_edge(START, "context")
        graph.add_edge("design_remote", "supervision")
        graph.add_edge("design_local", "supervision")
        graph.add_edge("supervision", "synthesis")
        graph.add_edge("synthesis", END)
        graph.add_conditional_edges(
            "context",
            self._select_design_path,
            {
                "remote": "hypothesis",
                "local": "hypothesis",
            },
        )
        graph.add_conditional_edges(
            "hypothesis",
            self._select_plan_mode,
            {
                "remote_enabled": "design_remote",
                "local_first": "design_local",
            },
        )
        return graph.compile()

    def _context_node(self, state: TacticalGraphState) -> TacticalGraphState:
        context = self.identity.build_context()
        self.last_context = context
        return {
            "context": context,
            "runtime": dict(self.last_runtime),
            "trace": self._append_trace(state, "context"),
        }

    def _select_design_path(self, state: TacticalGraphState) -> str:
        return "remote" if state["context"].openclaw_available else "local"

    def _hypothesis_node(self, state: TacticalGraphState) -> TacticalGraphState:
        hypothesis = self.hypothesis_agent.create(state["goal"], state["context"])
        return {
            "hypothesis": hypothesis,
            "trace": self._append_trace(state, "hypothesis"),
        }

    def _select_plan_mode(self, state: TacticalGraphState) -> str:
        context = state["context"]
        return "remote_enabled" if context.openclaw_available else "local_first"

    def _design_remote_node(self, state: TacticalGraphState) -> TacticalGraphState:
        experiment = self.design_agent.design(
            state["goal"],
            state["hypothesis"],
            state["context"],
            "remote_enabled",
        )
        return {
            "plan_mode": "remote_enabled",
            "experiment": experiment,
            "trace": self._append_trace(state, "design_remote"),
        }

    def _design_local_node(self, state: TacticalGraphState) -> TacticalGraphState:
        experiment = self.design_agent.design(
            state["goal"],
            state["hypothesis"],
            state["context"],
            "local_first",
        )
        return {
            "plan_mode": "local_first",
            "experiment": experiment,
            "trace": self._append_trace(state, "design_local"),
        }

    def _supervision_node(self, state: TacticalGraphState) -> TacticalGraphState:
        experiment, readiness = self.supervisor.evaluate(state["experiment"], state["context"])
        return {
            "experiment": experiment,
            "readiness": readiness,
            "trace": self._append_trace(state, "supervision"),
        }

    def _synthesis_node(self, state: TacticalGraphState) -> TacticalGraphState:
        trace = self._append_trace(state, "synthesis")
        runtime = dict(state.get("runtime", self.last_runtime))
        strategy = self.synthesis.build_strategy(
            state["goal"],
            state["experiment"],
            state["context"],
            trace,
        )
        strategy.artifacts.setdefault("graph", {})["runtime"] = runtime
        self.last_trace = trace
        self.last_strategy = strategy
        return {
            "strategy": strategy,
            "trace": trace,
        }

    def build_strategy(self, goal: StrategicGoal) -> Strategy:
        result = self.graph.invoke({"goal": goal, "trace": []})
        strategy = result["strategy"]
        if self.last_context is None:
            self.last_context = result.get("context")
        self.last_strategy = strategy
        self.last_trace = list(result.get("trace", []))
        return strategy

    def system_status(self) -> dict[str, object]:
        context = self.last_context or self.identity.build_context()
        return {
            "name": "El Tactico",
            "agents": [
                "hypothesis_agent",
                "experimental_design_agent",
                "supervision_and_analysis_agent",
                "synthesis_agent",
                "identity_uae",
            ],
            "frameworks": list(context.frameworks),
            "graph": {
                "engine": "langgraph",
                "nodes": [
                    "context",
                    "hypothesis",
                    "design_remote",
                    "design_local",
                    "supervision",
                    "synthesis",
                ],
                "last_trace": list(self.last_trace),
                "runtime": dict(self.last_runtime),
            },
            "status": "active" if context.openclaw_available else "degraded",
            "identity_email": context.identity_email,
            "openclaw": {
                "base_url": context.openclaw_base_url,
                "channel": context.openclaw_channel,
                "healthy": context.openclaw_available,
            },
            "ollama": {
                "base_url": context.ollama_base_url,
                "model": context.ollama_model,
                "healthy": context.ollama_available,
            },
            "capabilities": list(context.capabilities),
            "last_strategy": self.last_strategy.name if self.last_strategy else None,
        }
