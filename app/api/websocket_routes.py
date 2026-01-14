from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import os
import base64

from app.services.orchestrator_registry import orchestrators
from app.services.emotion_service import EmotionService
from app.services.speech_service import SpeechService
from app.utils.media_utils import decode_base64_image, save_base64_audio

router = APIRouter()

# --- INITIALIZE SERVICES ONCE (Global) ---
print("🚀 Initializing AI Services...")
emotion_service = EmotionService()
speech_service = SpeechService()
print("✅ AI Services Ready.")

@router.websocket("/ws/interview/{session_id}")
async def interview_websocket(websocket: WebSocket, session_id: str):
    """
    Multimodal WebSocket: Handles Text, Audio, and Video.
    """
    await websocket.accept()

    orchestrator = orchestrators.get(session_id)
    if not orchestrator:
        await websocket.close(code=1008)
        return

    # Local state for this connection to track emotion between frames
    latest_emotion = "neutral"
    latest_anomaly = None

    # Helper: Convert text response to audio and send
    async def send_ai_response(text: str, message_type: str = "question"):
        # 1. Generate Audio (TTS)
        output_filename = f"response_{session_id}.mp3"
        await speech_service.text_to_speech(text, output_filename)
        
        # 2. Read Audio -> Base64
        audio_b64 = ""
        if os.path.exists(output_filename):
            with open(output_filename, "rb") as audio_file:
                audio_b64 = base64.b64encode(audio_file.read()).decode("utf-8")
            os.remove(output_filename) # Cleanup

        # 3. Send JSON
        await websocket.send_json({
            "type": message_type,
            "payload": {
                "text": text,
                "audio": f"data:audio/mp3;base64,{audio_b64}", # Frontend needs this format
                "emotion_context": latest_emotion 
            }
        })

    try:
        # 🔹 1. Send Initial Greeting (with Audio)
        greeting = "Hello! I am your AI interviewer. I am verifying your camera and microphone. Let's start."
        await send_ai_response(greeting, "info")

        while True:
            # 🔹 2. Listen for messages
            data = await websocket.receive_json()
            msg_type = data.get("type")
            payload = data.get("payload", {})

            # ----------------------------------------
            # TYPE A: VIDEO FRAME (Background Monitoring)
            # ----------------------------------------
            if msg_type == "video_frame":
                image_b64 = payload.get("image", "")
                if image_b64:
                    # Run emotion analysis in a separate thread to avoid lag
                    frame = decode_base64_image(image_b64)
                    if frame is not None:
                        analysis = await asyncio.to_thread(emotion_service.analyze_frame, frame)
                        
                        latest_emotion = analysis["emotion"]
                        latest_anomaly = analysis["anomaly"]
                        
                        # If huge anomaly, warn frontend immediately
                        if latest_anomaly:
                             await websocket.send_json({
                                 "type": "warning",
                                 "payload": {"message": latest_anomaly}
                             })
                continue # Don't process interview logic for video frames

            # ----------------------------------------
            # TYPE B: AUDIO ANSWER (User Speaking)
            # ----------------------------------------
            elif msg_type == "audio_answer":
                audio_b64 = payload.get("audio_data", "")
                
                # 1. Save & Transcribe (STT)
                temp_audio_file = save_base64_audio(audio_b64)
                if temp_audio_file:
                    candidate_text = await asyncio.to_thread(speech_service.speech_to_text, temp_audio_file)
                    
                    # Cleanup temp input file
                    if os.path.exists(temp_audio_file):
                        os.remove(temp_audio_file)
                else:
                    candidate_text = ""

                if not candidate_text:
                    await websocket.send_json({"type": "error", "payload": {"message": "I couldn't hear you."}})
                    continue

                # 2. Run Interview Logic (LangGraph)
                # We inject the 'latest_emotion' we captured from the video frames
                response = await asyncio.to_thread(
                    orchestrator.run_step,
                    candidate_id=session_id,
                    candidate_answer=candidate_text,
                    emotion_state=latest_emotion
                )

                # 3. Handle End of Interview
                if response["interview_status"] == "ended":
                    await send_ai_response("Thank you for your time. The interview is finished.", "interview_end")
                    break

                # 4. Send Next Question (Text + Audio)
                await send_ai_response(response["next_question"])

            # ----------------------------------------
            # TYPE C: TEXT ANSWER (Fallback)
            # ----------------------------------------
            elif msg_type == "answer":
                text_answer = payload.get("text", "")
                
                response = await asyncio.to_thread(
                    orchestrator.run_step,
                    candidate_id=session_id,
                    candidate_answer=text_answer,
                    emotion_state=latest_emotion
                )
                
                if response["interview_status"] == "ended":
                    await send_ai_response("Interview finished.", "interview_end")
                    break
                    
                await send_ai_response(response["next_question"])

    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        print(f"WebSocket Error: {e}")
        await websocket.close()
    finally:
        pass











#V1
# # app/api/websocket_routes.py

# from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# import uuid
# from app.services.orchestrator_registry import orchestrators

# from app.agents.orchestrator import InterviewOrchestrator

# router = APIRouter()

# # Active WebSocket interview sessions
# #active_sessions: dict[str, InterviewOrchestrator] = {}
# active_sessions = orchestrators

# @router.websocket("/ws/interview/{session_id}")
# async def interview_websocket(websocket: WebSocket, session_id: str):
#     """
#     WebSocket endpoint for live AI interview.
#     """

#     await websocket.accept()

#     # Create a unique session ID
#     #session_id = str(uuid.uuid4())

#     # Create orchestrator for this interview
#     #orchestrator = InterviewOrchestrator()

#     orchestrator = orchestrators.get(session_id)
#     if not orchestrator:
#         await websocket.close(code=1008)
#         return


#     #active_sessions[session_id] = orchestrator

#     try:
#         # 🔹 Send initial greeting / first question trigger
#         await websocket.send_json({
#             "type": "info",
#             "payload": {
#                 "message": "Interview is getting started. Shall we start?."
#             }
#         })

#         while True:
#             # 🔹 Receive candidate message
#             data = await websocket.receive_json()

#             msg_type = data.get("type")
#             payload = data.get("payload", {})

#             if msg_type != "answer":
#                 await websocket.send_json({
#                     "type": "error",
#                     "payload": {"message": "Invalid message type"}
#                 })
#                 continue

#             candidate_answer = payload.get("text", "").strip()

#             if not candidate_answer:
#                 await websocket.send_json({
#                     "type": "error",
#                     "payload": {"message": "Answer cannot be empty"}
#                 })
#                 continue

#             # 🔹 Run one interview step
#             response = orchestrator.run_step(
#                 candidate_id=session_id,
#                 candidate_answer=candidate_answer
#             )

#             # 🔹 Check interview status
#             if response["interview_status"] == "ended":
#                 await websocket.send_json({
#                     "type": "interview_end",
#                     "payload": {
#                         "message": "Interview completed. Thank you!"
#                     }
#                 })
#                 break

#             # 🔹 Send next question
#             await websocket.send_json({
#                 "type": "question",
#                 "payload": {
#                     "text": response["next_question"],
#                     "round": response["interview_round"]
#                 }
#             })

#     except WebSocketDisconnect:
#         print(f"WebSocket disconnected: {session_id}")

#     finally:
#         # 🔹 Cleanup session
#         #active_sessions.pop(session_id, None)
#         await websocket.close()
