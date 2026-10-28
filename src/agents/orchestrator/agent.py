"""Orchestrator Agent — Central task planner and router using LangGraph.

This agent receives user input, decomposes it into sub-tasks, routes them to
specialist agents (vision, nlp, rag, prediction), aggregates results, and
passes them to the GenAI synthesis layer.
"""

import operator
import time
from typing import Annotated, Any, Callable, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from src.agents.base import BaseAgent
from src.agents.display import NODE_DISPLAY
from src.agents.nlp.agent import NLPAgent
from src.agents.vision.agent import VisionAgent
from src.agents.rag.agent import RAGAgent
from src.agents.prediction.agent import PredictionAgent
from src.agents.synthesis.agent import GenAIAgent
from src.utils.redaction import safe_error, text_fingerprint
from config import settings

__all__ = ["NODE_DISPLAY", "DiagnosticState", "OrchestratorAgent"]


class DiagnosticState(BaseModel):
    """Shared state passed between all nodes in the orchestrator graph."""

    user_input: str = ""
    symptoms: list[str] = Field(default_factory=list)
    image_path: Optional[str] = None
    patient_history: Optional[dict] = None
    voice_transcript: Optional[str] = None

    # Agent outputs
    vision_result: Optional[dict] = None
    nlp_result: Optional[dict] = None
    rag_result: Optional[dict] = None
    prediction_result: Optional[dict] = None

    # Final output
    synthesis_result: Optional[dict] = None
    confidence_score: float = 0.0
    severity: str = "unknown"
    doctor_alert: bool = False

    # Execution tracking
    tasks_to_run: list[str] = Field(default_factory=list)
    # Additive reducer: every node contributes its own failures instead of
    # overwriting the errors collected by the nodes that ran before it.
    errors: Annotated[list[str], operator.add] = Field(default_factory=list)

    # Live execution progress callback. Carried on the state so graph nodes
    # can publish lifecycle events; it is stripped from the returned result.
    progress_cb: Optional[Callable[[dict], None]] = None


class OrchestratorAgent(BaseAgent):
    """LangGraph-based orchestrator that plans and routes diagnostic tasks."""

    name = "orchestrator_agent"
    description = "Plans tasks, routes to sub-agents, manages memory, reasons step-by-step"

    def __init__(self):
        super().__init__()
        # Initialize agents with lazy loading — heavy models not loaded at startup
        self.nlp_agent = NLPAgent()
        self.vision_agent = VisionAgent()
        self.rag_agent = RAGAgent()
        self.prediction_agent = PredictionAgent()
        self.synthesis_agent = GenAIAgent()
        self.graph = self._build_graph()
        self.log("info", "Orchestrator agent initialized (models loaded lazily on first use)")

    def _build_graph(self):
        """Build the LangGraph workflow for diagnostic orchestration.

        The routing decision determines which specialist nodes run; every
        node is guarded by that decision, so the graph executes only the
        agents the input calls for. Nodes run in sequence rather than
        fanning out in parallel: specialist models are heavy, and loading
        them concurrently causes memory spikes on the CPU-only deployment.
        """
        workflow = StateGraph(DiagnosticState)

        workflow.add_node("route_decision", self._node_route_decision)
        workflow.add_node("analyze_symptoms", self._graph_symptoms)
        workflow.add_node("retrieve_knowledge", self._graph_knowledge)
        workflow.add_node("analyze_image", self._graph_image)
        workflow.add_node("assess_risk", self._graph_risk)
        workflow.add_node("synthesize", self._graph_synthesis)

        workflow.set_entry_point("route_decision")
        workflow.add_edge("route_decision", "analyze_symptoms")
        workflow.add_edge("analyze_symptoms", "retrieve_knowledge")
        workflow.add_edge("retrieve_knowledge", "analyze_image")
        workflow.add_edge("analyze_image", "assess_risk")
        workflow.add_edge("assess_risk", "synthesize")
        workflow.add_edge("synthesize", END)

        return workflow.compile()

    async def run(self, input_data: dict, progress_cb: Optional[Callable[[dict], None]] = None) -> dict:
        """Execute the full diagnostic orchestration pipeline.

        Args:
            input_data: Dict with keys like 'text', 'image_path', 'patient_history'.
            progress_cb: Optional callable receiving lifecycle event dicts
                (planned, agent started/completed/failed) for live streaming.

        Returns:
            Complete diagnostic result with findings, confidence, and alerts.
        """
        state = DiagnosticState(
            user_input=input_data.get("text", ""),
            image_path=input_data.get("image_path"),
            patient_history=input_data.get("patient_history"),
            voice_transcript=input_data.get("voice_transcript"),
            progress_cb=progress_cb,
        )

        final_state = await self.graph.ainvoke(state)
        return {key: value for key, value in final_state.items() if key != "progress_cb"}

    def _emit(self, progress_cb: Optional[Callable[[dict], None]], node: str, status: str, **extra) -> None:
        """Publish a lifecycle event for one graph node (no-op without callback)."""
        if progress_cb is None:
            return
        event = {"type": "agent", "node": node, "status": status}
        event.update(NODE_DISPLAY.get(node, {}))
        event.update(extra)
        try:
            progress_cb(event)
        except Exception as e:
            self.log("debug", f"Progress callback failed: {e}")

    async def _run_graph_task(
        self,
        state: DiagnosticState,
        task: str,
        worker: Callable[[DiagnosticState], Any],
    ) -> dict:
        """Run one specialist node with lifecycle events and timing.

        The node's own return value is handed back to LangGraph, which
        merges it into the shared state (the ``errors`` field uses an
        additive reducer, so failures accumulate across nodes).
        """
        started = time.perf_counter()
        self._emit(state.progress_cb, task, "started")
        try:
            result = await worker(state)
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
            self.log("error", f"Node {task} raised: {safe_error(e)}")
            self._emit(
                state.progress_cb, task, "failed",
                elapsed_ms=elapsed_ms, summary=str(e)[:160],
            )
            return {"errors": [str(e)]}

        elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
        failed = bool(result.get("errors"))
        self._emit(
            state.progress_cb, task, "failed" if failed else "completed",
            elapsed_ms=elapsed_ms,
            summary=self._node_summary(task, state, result),
        )
        return result

    async def _graph_symptoms(self, state: DiagnosticState) -> dict:
        """Graph node: symptom extraction, when the input calls for it."""
        if "symptoms" not in state.tasks_to_run:
            return {}
        return await self._run_graph_task(state, "symptoms", self._node_nlp_analysis)

    async def _graph_knowledge(self, state: DiagnosticState) -> dict:
        """Graph node: knowledge retrieval, when the input calls for it."""
        if "knowledge" not in state.tasks_to_run:
            return {}
        return await self._run_graph_task(state, "knowledge", self._node_rag_retrieval)

    async def _graph_image(self, state: DiagnosticState) -> dict:
        """Graph node: image analysis, when an image was supplied."""
        if "image" not in state.tasks_to_run:
            return {}
        return await self._run_graph_task(state, "image", self._node_vision_analysis)

    async def _graph_risk(self, state: DiagnosticState) -> dict:
        """Graph node: risk scoring, when patient history is available."""
        if "risk" not in state.tasks_to_run:
            return {}
        return await self._run_graph_task(state, "risk", self._node_prediction)

    async def _graph_synthesis(self, state: DiagnosticState) -> dict:
        """Graph node: report synthesis (always runs last)."""
        started = time.perf_counter()
        self._emit(state.progress_cb, "synthesis", "started")
        result = await self._node_synthesis(state)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
        failed = bool(result.get("errors"))
        self._emit(
            state.progress_cb, "synthesis", "failed" if failed else "completed",
            elapsed_ms=elapsed_ms,
            summary=(
                f"severity: {result.get('severity', 'unknown')}, "
                f"confidence: {round((result.get('confidence_score') or 0) * 100)}%"
            ),
        )
        return result

    def _node_summary(self, task: str, state: DiagnosticState, result: dict) -> str:
        """One-line human-readable outcome for a finished node."""
        if result.get("errors"):
            return "completed with fallback data"
        if task == "symptoms":
            symptoms = result.get("symptoms", state.symptoms)
            return f"{len(symptoms)} symptom(s) extracted"
        if task == "image":
            findings = (result.get("vision_result") or {}).get("total_detected", 0)
            return f"{findings} finding(s) detected"
        if task == "knowledge":
            docs = len((result.get("rag_result") or {}).get("relevant_docs", []) or [])
            return f"{docs} source(s) retrieved"
        if task == "risk":
            risks = (result.get("prediction_result") or {}).get("risk_scores", {})
            return f"{len(risks)} risk factor(s) scored" if isinstance(risks, dict) else "risk scored"
        return "done"

    async def _node_route_decision(self, state: DiagnosticState) -> dict:
        """Decide which specialist agents to invoke based on available input."""
        tasks = []
        if state.user_input or state.voice_transcript:
            tasks.append("symptoms")
            tasks.append("knowledge")
        if state.image_path:
            tasks.append("image")
        if state.patient_history:
            tasks.append("risk")

        if state.progress_cb is not None:
            state.progress_cb({"type": "planned", "tasks": list(tasks)})

        return {"tasks_to_run": tasks}

    async def _node_nlp_analysis(self, state: DiagnosticState) -> dict:
        """Call NLP agent for symptom extraction."""
        text = state.user_input or state.voice_transcript or ""
        self.log("info", f"Routing to NLP agent — input {text_fingerprint(text)}")
        try:
            result = await self.nlp_agent.run({"text": text})
            return {
                "nlp_result": result,
                "symptoms": [s.get("symptom", s) if isinstance(s, dict) else s for s in result.get("symptoms", [])],
            }
        except Exception as e:
            self.log("error", f"NLP agent failed: {safe_error(e, text)}")
            return {"nlp_result": {"symptoms": [], "entities": [], "error": str(e)}, "errors": [str(e)]}

    async def _node_vision_analysis(self, state: DiagnosticState) -> dict:
        """Call Vision agent for image analysis."""
        self.log("info", f"Routing to Vision agent — image {text_fingerprint(state.image_path)}")
        try:
            result = await self.vision_agent.run({"image_path": state.image_path})
            return {"vision_result": result}
        except Exception as e:
            self.log("error", f"Vision agent failed: {safe_error(e)}")
            return {"vision_result": {"findings": [], "confidence": 0.0, "anomalies": [], "error": str(e)}, "errors": [str(e)]}

    async def _node_rag_retrieval(self, state: DiagnosticState) -> dict:
        """Call RAG agent for medical knowledge retrieval."""
        self.log("info", "Routing to RAG agent")
        try:
            query = state.user_input or " ".join(state.symptoms)
            result = await self.rag_agent.run({"query": query, "symptoms": state.symptoms})
            return {"rag_result": result}
        except Exception as e:
            self.log("error", f"RAG agent failed: {safe_error(e, query)}")
            return {"rag_result": {"relevant_docs": [], "knowledge": "", "error": str(e)}, "errors": [str(e)]}

    async def _node_prediction(self, state: DiagnosticState) -> dict:
        """Call Prediction agent for risk scoring."""
        self.log("info", "Routing to Prediction agent")
        try:
            result = await self.prediction_agent.run({
                "patient_history": state.patient_history or {},
                "symptoms": state.symptoms,
            })
            return {"prediction_result": result}
        except Exception as e:
            self.log("error", f"Prediction agent failed: {safe_error(e)}")
            return {"prediction_result": {"risk_scores": {}, "severity": "unknown", "error": str(e)}, "errors": [str(e)]}

    async def _node_synthesis(self, state: DiagnosticState) -> dict:
        """Merge all agent outputs and generate final diagnostic report."""
        self.log("info", "Running GenAI synthesis")
        try:
            # Build patient context string
            patient_context = ""
            if state.patient_history:
                parts = []
                if "age" in state.patient_history:
                    parts.append(f"Age: {state.patient_history['age']}")
                if "gender" in state.patient_history:
                    parts.append(f"Gender: {state.patient_history['gender']}")
                if "bmi" in state.patient_history:
                    parts.append(f"BMI: {state.patient_history['bmi']}")
                if "conditions" in state.patient_history:
                    parts.append(f"Existing conditions: {', '.join(state.patient_history['conditions'])}")
                if "family_history" in state.patient_history:
                    parts.append(f"Family history: {', '.join(state.patient_history['family_history'])}")
                patient_context = "\n".join(parts)

            synthesis_input = {
                "nlp": state.nlp_result or {},
                "vision": state.vision_result or {},
                "rag": state.rag_result or {},
                "prediction": state.prediction_result or {},
                "patient_context": patient_context,
                "user_input": state.user_input,
            }

            result = await self.synthesis_agent.run(synthesis_input)

            return {
                "synthesis_result": result,
                "confidence_score": result.get("confidence", {}).get("overall_confidence", 0.0),
                "severity": result.get("severity", "unknown"),
                "doctor_alert": result.get("doctor_alert", False),
            }
        except Exception as e:
            self.log("error", f"Synthesis failed: {e}")
            return {
                "synthesis_result": {
                    "diagnosis": [],
                    "explanation": f"An error occurred during report generation: {str(e)}",
                    "recommendations": ["Consult a healthcare professional"],
                    "severity": "unknown",
                    "doctor_alert": False,
                    "disclaimer": "This is an AI-generated assessment and not a substitute for professional medical advice.",
                },
                "confidence_score": 0.0,
                "severity": "unknown",
                "doctor_alert": False,
                "errors": [str(e)],
            }
