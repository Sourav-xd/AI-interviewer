import websocket
import json
import threading
import time
import cv2
import base64
import requests
import os

# Configuration
API_URL = "http://localhost:8000/interviews/start"
WS_BASE_URL = "ws://localhost:8000/ws/interview"
# Make sure this path is 100% correct
TEST_AUDIO_FILE = "C:\\Users\\sjoshi06\\OneDrive - dentsu\\Desktop\\AI-interviewer\\test_answer.mp3"

def get_session_id():
    """Call the API to start an interview"""
    try:
        response = requests.post(API_URL)
        if response.status_code == 200:
            return response.json()["session_id"]
    except Exception as e:
        print(f"❌ API Error: {e}")
    return None

def on_message(ws, message):
    data = json.loads(message)
    msg_type = data.get("type")
    payload = data.get("payload", {})

    print(f"\n📩 RECEIVED [Type: {msg_type}]")
    
    # --- CASE 1: Initial Greeting (INFO) ---
    if msg_type == "info":
        # FIXED: Backend sends 'text', not 'message'
        print(f"ℹ️ Info: {payload.get('text')}")
        
        # TRIGGER: Respond to the greeting to start the loop!
        print("🗣️ Responding to greeting...")
        time.sleep(1) 
        send_audio_response(ws)
        
    # --- CASE 2: AI Asks Question ---
    elif msg_type == "question":
        text = payload.get("text")
        print(f"🤖 AI Question: {text}")
        
        # Save audio
        audio_b64 = payload.get("audio")
        if audio_b64:
            save_audio_response(audio_b64)

        # TRIGGER: Respond to the question
        print("⏳ Thinking (2s)...")
        time.sleep(2)
        send_audio_response(ws)

    # --- CASE 3: Interview Ended ---
    elif msg_type == "interview_end":
        print(f"🏁 END: {payload.get('text')}")
        ws.close() # Stop the loop

    elif msg_type == "warning":
        # Ignore repeated face warnings to keep console clean
        pass 

    elif msg_type == "error":
        print(f"❌ ERROR: {payload.get('message')}")

def save_audio_response(audio_b64):
    if "," in audio_b64:
        audio_b64 = audio_b64.split(",")[1]
    filename = f"response_{int(time.time())}.mp3"
    with open(filename, "wb") as f:
        f.write(base64.b64decode(audio_b64))
    print(f"🔊 Audio saved to '{filename}'")

def send_audio_response(ws):
    if not os.path.exists(TEST_AUDIO_FILE):
        print(f"❌ File not found: {TEST_AUDIO_FILE}")
        return

    print(f"🎙️ Sending Audio Answer...")
    with open(TEST_AUDIO_FILE, "rb") as audio_file:
        encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
    
    msg = {
        "type": "audio_answer",
        "payload": {"audio_data": f"data:audio/mp3;base64,{encoded_string}"}
    }
    ws.send(json.dumps(msg))

def on_open(ws):
    print("✅ Connected! Starting Video Stream...")
    threading.Thread(target=send_video_stream, args=(ws,), daemon=True).start()

def send_video_stream(ws):
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        
        try:
            ws.send(json.dumps({
                "type": "video_frame", 
                "payload": {"image": f"data:image/jpeg;base64,{jpg_as_text}"}
            }))
        except:
            break
        time.sleep(1.5) # Slow down video to reduce log spam
    cap.release()

if __name__ == "__main__":
    session_id = get_session_id()
    if session_id:
        print(f"🔌 Connecting to Session: {session_id}")
        ws = websocket.WebSocketApp(f"{WS_BASE_URL}/{session_id}",
                                    on_open=on_open,
                                    on_message=on_message)
        ws.run_forever()






# import websocket
# import json
# import threading
# import time
# import cv2
# import base64
# import uuid

# # Configuration
# SESSION_ID = str(uuid.uuid4())
# WS_URL = f"ws://localhost:8000/ws/interview/{SESSION_ID}"
# TEST_AUDIO_FILE = "C:\\Users\\sjoshi06\\OneDrive - dentsu\\Desktop\\AI-interviewer\\test_answer.mp3"  # Make sure this file exists!

# def on_message(ws, message):
#     data = json.loads(message)
#     msg_type = data.get("type")
#     payload = data.get("payload", {})

#     print(f"\n📩 RECEIVED [Type: {msg_type}]")
    
#     if msg_type == "info":
#         print(f"ℹ️ Info: {payload.get('message')}")
        
#     elif msg_type == "question":
#         text = payload.get("text")
#         print(f"🤖 AI Question: {text}")
        
#         # Save the audio response to verify TTS worked
#         audio_b64 = payload.get("audio")
#         if audio_b64:
#             if "," in audio_b64:
#                 audio_b64 = audio_b64.split(",")[1]
#             with open(f"response_{int(time.time())}.mp3", "wb") as f:
#                 f.write(base64.b64decode(audio_b64))
#             print("🔊 Audio saved to 'response_timestamp.mp3'. Play it to hear the AI!")

#         # --- SIMULATE USER ANSWERING ---
#         # Wait 2 seconds, then send the dummy audio file
#         time.sleep(2)
#         send_audio_response(ws)

#     elif msg_type == "warning":
#         print(f"⚠️ WARNING: {payload.get('message')}")
        
#     elif msg_type == "error":
#         print(f"❌ ERROR: {payload.get('message')}")

# def on_error(ws, error):
#     print(f"Error: {error}")

# def on_close(ws, close_status_code, close_msg):
#     print("### Connection Closed ###")

# def on_open(ws):
#     print("✅ Connected to Backend!")
    
#     # Start sending video frames in the background
#     threading.Thread(target=send_video_stream, args=(ws,), daemon=True).start()

# # --- HELPER: Send Video Frames (Simulates Webcam) ---
# def send_video_stream(ws):
#     cap = cv2.VideoCapture(0)
#     print("📷 Camera Capture Started (Sending frames every 1s)...")
    
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret: break
        
#         # Encode frame to JPEG -> Base64
#         _, buffer = cv2.imencode('.jpg', frame)
#         jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        
#         # Send to WebSocket
#         msg = {
#             "type": "video_frame",
#             "payload": {
#                 "image": f"data:image/jpeg;base64,{jpg_as_text}"
#             }
#         }
#         try:
#             ws.send(json.dumps(msg))
#             # print(".", end="", flush=True) # visual heartbeat
#         except:
#             break
            
#         time.sleep(1.0) # Limit to 1 frame per second
    
#     cap.release()

# # --- HELPER: Send Audio (Simulates Mic) ---
# def send_audio_response(ws):
#     if not os.path.exists(TEST_AUDIO_FILE):
#         print(f"\n❌ ALERT: '{TEST_AUDIO_FILE}' not found. Cannot send audio answer.")
#         return

#     print(f"\n🎙️ Sending Audio Answer ({TEST_AUDIO_FILE})...")
#     with open(TEST_AUDIO_FILE, "rb") as audio_file:
#         encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
    
#     msg = {
#         "type": "audio_answer",
#         "payload": {
#             "audio_data": f"data:audio/mp3;base64,{encoded_string}"
#         }
#     }
#     ws.send(json.dumps(msg))
#     print("✅ Audio Sent!")

# if __name__ == "__main__":
#     import os
    
#     # Check if backend is running
#     print(f"Connecting to {WS_URL}...")
#     print("Make sure your FastAPI server is running! (uvicorn app.main:app --reload)")
    
#     # Start WebSocket Client
#     ws = websocket.WebSocketApp(WS_URL,
#                                 on_open=on_open,
#                                 on_message=on_message,
#                                 on_error=on_error,
#                                 on_close=on_close)
#     ws.run_forever()