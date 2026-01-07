# app/api/interview_routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.orchestrator_registry import orchestrators
from app.services.memory_service import memory_service

router = APIRouter(prefix="/interviews", tags=["Interviews"])


# ---------------------------
# Response Models
# ---------------------------

class StartInterviewResponse(BaseModel):
    session_id: str
    status: str
    max_rounds: int


class InterviewStatusResponse(BaseModel):
    session_id: str
    status: str
    round: int


class InterviewSummaryResponse(BaseModel):
    session_id: str
    status: str
    strengths: list[str]
    weaknesses: list[str]
    total_rounds: int


# ---------------------------
# Routes
# ---------------------------

@router.post("/start", response_model=StartInterviewResponse)
def start_interview():
    """
    Create a new interview session.
    """
    import uuid
    from app.agents.orchestrator import InterviewOrchestrator
    from app.models.interview_state import create_initial_state

    session_id = str(uuid.uuid4())
    #orchestrators[session_id] = InterviewOrchestrator()
    
    orchestrator = InterviewOrchestrator()
    orchestrator.sessions[session_id] = create_initial_state(session_id)

    orchestrators[session_id] = orchestrator




    return {
        "session_id": session_id,
        "status": "ongoing",
        "max_rounds": 5
    }


@router.get("/{session_id}/status", response_model=InterviewStatusResponse)
def get_interview_status(session_id: str):
    """
    Get current status of an interview.
    """
    orchestrator = orchestrators.get(session_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Interview not found")

    state = orchestrator.sessions.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Interview state not found")

    return {
        "session_id": session_id,
        "status": state.interview_status,
        "round": state.interview_round
    }


@router.get("/{session_id}/summary", response_model=InterviewSummaryResponse)
def get_interview_summary(session_id: str):
    """
    Fetch post-interview summary.
    """
    orchestrator = orchestrators.get(session_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Interview not found")

    state = orchestrator.sessions.get(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Interview state not found")

    profile = memory_service.summarize_candidate_profile()

    return {
        "session_id": session_id,
        "status": state.interview_status,
        "strengths": profile["strengths"],
        "weaknesses": profile["weaknesses"],
        "total_rounds": state.interview_round
    }


@router.get("/active")
def get_active_interviews():
    """
    List active interview session IDs.
    """
    return {
        "active_sessions": list(orchestrators.keys())
    }


@router.get("/health")
def health_check():
    return {"status": "ok"}
