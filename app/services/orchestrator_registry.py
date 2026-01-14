# app/services/orchestrator_registry.py
from app.agents.orchestrator import InterviewOrchestrator

# Global orchestrator registry
orchestrators: dict[str, InterviewOrchestrator] = {}
