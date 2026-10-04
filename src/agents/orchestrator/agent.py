"""Orchestrator Agent — Central task planner and router using LangGraph.

This agent receives user input, decomposes it into sub-tasks, routes them to
specialist agents (vision, nlp, rag, prediction), aggregates results, and
passes them to the GenAI synthesis layer.
"""

from typing import Any, Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from src.agents.base import BaseAgent
from src.agents.nlp.agent import NLPAgent
from src.agents.vision.agent import VisionAgent
from src.agents.rag.agent import RAGAgent
from src.agents.prediction.agent import PredictionAgent
from src.agents.synthesis.agent import GenAIAgent
from config import settings


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
    errors: list[str] = Field(default_factory=list)


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

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for diagnostic orchestration."""
        workflow = StateGraph(DiagnosticState)

        # Add nodes (each calls a specialist agent)
        workflow.add_node("analyze_symptoms", self._node_nlp_analysis)
        workflow.add_node("analyze_image", self._node_vision_analysis)
        workflow.add_node("retrieve_knowledge", self._node_rag_retrieval)
        workflow.add_node("assess_risk", self._node_prediction)
        workflow.add_node("route_decision", self._node_route_decision)
        workflow.add_node("synthesize", self._node_synthesis)

        # Entry point
        workflow.set_entry_point("route_decision")

        # Conditional routing
        workflow.add_conditional_edges(
            "route_decision",
            self._route_to_agents,
            {
                "symptoms": "analyze_symptoms",
                "image": "analyze_image",
                "knowledge": "retrieve_knowledge",
                "risk": "assess_risk",
            },
        )

        # All analysis nodes converge to synthesis
        for node in ["analyze_symptoms", "analyze_image", "retrieve_knowledge", "assess_risk"]:
            workflow.add_edge(node, "synthesize")

        workflow.add_edge("synthesize", END)

        return workflow.compile()

    async def run(self, input_data: dict) -> dict:
        """Execute the full diagnostic orchestration pipeline.

        Args:
            input_data: Dict with keys like 'text', 'image_path', 'patient_history'.

        Returns:
            Complete diagnostic result with findings, confidence, and alerts.
        """
        state = DiagnosticState(
            user_input=input_data.get("text", ""),
            image_path=input_data.get("image_path"),
            patient_history=input_data.get("patient_history"),
            voice_transcript=input_data.get("voice_transcript"),
        )

        # Run orchestration steps sequentially to avoid memory spikes
        # from concurrent model loading
        result = await self._run_sequential(state)
        return result

    async def _run_sequential(self, state: DiagnosticState) -> dict:
        """Run agents sequentially to manage memory usage."""
        # Route decision
        route_result = self._node_route_decision(state)
        state.tasks_to_run = route_result.get("tasks_to_run", [])

        # Run each agent sequentially
        for task in state.tasks_to_run:
            if task == "symptoms":
                result = await self._node_nlp_analysis(state)
                state.nlp_result = result.get("nlp_result")
                state.symptoms = result.get("symptoms", [])
                if result.get("errors"):
                    state.errors.extend(result["errors"])
            elif task == "image":
                result = await self._node_vision_analysis(state)
                state.vision_result = result.get("vision_result")
                if result.get("errors"):
                    state.errors.extend(result["errors"])
            elif task == "knowledge":
                result = await self._node_rag_retrieval(state)
                state.rag_result = result.get("rag_result")
                if result.get("errors"):
                    state.errors.extend(result["errors"])
            elif task == "risk":
                result = await self._node_prediction(state)
                state.prediction_result = result.get("prediction_result")
                if result.get("errors"):
                    state.errors.extend(result["errors"])

        # Synthesis (always runs last)
        result = await self._node_synthesis(state)
        state.synthesis_result = result.get("synthesis_result")
        state.confidence_score = result.get("confidence_score", 0.0)
        state.severity = result.get("severity", "unknown")
        state.doctor_alert = result.get("doctor_alert", False)
        if result.get("errors"):
            state.errors.extend(result["errors"])

        return state.dict()

    def _node_route_decision(self, state: DiagnosticState) -> dict:
        """Decide which specialist agents to invoke based on available input."""
        tasks = []
        if state.user_input or state.voice_transcript:
            tasks.append("symptoms")
            tasks.append("knowledge")
        if state.image_path:
            tasks.append("image")
        if state.patient_history:
            tasks.append("risk")

        return {"tasks_to_run": tasks}

    def _route_to_agents(self, state: DiagnosticState) -> list[str]:
        """Return list of task names to execute (mapped to nodes by LangGraph)."""
        return state.tasks_to_run

    async def _node_nlp_analysis(self, state: DiagnosticState) -> dict:
        """Call NLP agent for symptom extraction."""
        self.log("info", f"Routing to NLP agent — input: {state.user_input[:100]}")
        try:
            text = state.user_input or state.voice_transcript or ""
            result = await self.nlp_agent.run({"text": text})
            return {
                "nlp_result": result,
                "symptoms": [s.get("symptom", s) if isinstance(s, dict) else s for s in result.get("symptoms", [])],
            }
        except Exception as e:
            self.log("error", f"NLP agent failed: {e}")
            return {"nlp_result": {"symptoms": [], "entities": [], "error": str(e)}, "errors": [str(e)]}

    async def _node_vision_analysis(self, state: DiagnosticState) -> dict:
        """Call Vision agent for image analysis."""
        self.log("info", f"Routing to Vision agent — image: {state.image_path}")
        try:
            result = await self.vision_agent.run({"image_path": state.image_path})
            return {"vision_result": result}
        except Exception as e:
            self.log("error", f"Vision agent failed: {e}")
            return {"vision_result": {"findings": [], "confidence": 0.0, "anomalies": [], "error": str(e)}, "errors": [str(e)]}

    async def _node_rag_retrieval(self, state: DiagnosticState) -> dict:
        """Call RAG agent for medical knowledge retrieval."""
        self.log("info", "Routing to RAG agent")
        try:
            query = state.user_input or " ".join(state.symptoms)
            result = await self.rag_agent.run({"query": query, "symptoms": state.symptoms})
            return {"rag_result": result}
        except Exception as e:
            self.log("error", f"RAG agent failed: {e}")
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
            self.log("error", f"Prediction agent failed: {e}")
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
