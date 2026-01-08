# app/api/websocket_routes.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import uuid
from app.services.orchestrator_registry import orchestrators

from app.agents.orchestrator import InterviewOrchestrator

router = APIRouter()

# Active WebSocket interview sessions
#active_sessions: dict[str, InterviewOrchestrator] = {}
active_sessions = orchestrators

@router.websocket("/ws/interview/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for live AI interview.
    """

    await websocket.accept()

    # Create a unique session ID
    #session_id = str(uuid.uuid4())

    # Create orchestrator for this interview
    #orchestrator = InterviewOrchestrator()

    orchestrator = orchestrators.get(session_id)
    if not orchestrator:
        await websocket.close(code=1008)
        return


    #active_sessions[session_id] = orchestrator

    try:
        # 🔹 Send initial greeting / first question trigger
        await websocket.send_json({
            "type": "info",
            "payload": {
                "message": "Interview is getting started. Shall we start?."
            }
        })

        while True:
            # 🔹 Receive candidate message
            data = await websocket.receive_json()

            msg_type = data.get("type")
            payload = data.get("payload", {})

            if msg_type != "answer":
                await websocket.send_json({
                    "type": "error",
                    "payload": {"message": "Invalid message type"}
                })
                continue

            candidate_answer = payload.get("text", "").strip()

            if not candidate_answer:
                await websocket.send_json({
                    "type": "error",
                    "payload": {"message": "Answer cannot be empty"}
                })
                continue

            # 🔹 Run one interview step
            response = orchestrator.run_step(
                candidate_id=session_id,
                candidate_answer=candidate_answer
            )

            # 🔹 Check interview status
            if response["interview_status"] == "ended":
                await websocket.send_json({
                    "type": "interview_end",
                    "payload": {
                        "message": "Interview completed. Thank you!"
                    }
                })
                break

            # 🔹 Send next question
            await websocket.send_json({
                "type": "question",
                "payload": {
                    "text": response["next_question"],
                    "round": response["interview_round"]
                }
            })

    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {session_id}")

    finally:
        # 🔹 Cleanup session
        #active_sessions.pop(session_id, None)
        await websocket.close()
