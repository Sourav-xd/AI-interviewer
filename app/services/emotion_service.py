# app/services/emotion_service.py
import cv2
from deepface import DeepFace
import numpy as np

class EmotionService:
    def __init__(self):
        # Load OpenCV's built-in face detector (Haar Cascade)
        # This is extremely stable and does not require external downloads
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        print("✅ Emotion Service Loaded")

    def analyze_frame(self, frame):
        # 1. Convert to Grayscale (Needed for detection)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 2. Detect Faces
        faces = self.face_cascade.detectMultiScale(
            gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        analysis = {
            "face_detected": False,
            "face_count": 0,
            "anomaly": None,
            "emotion": "neutral",
            "emotion_score": 0.0,
            "face_coords": [] 
        }

        if len(faces) > 0:
            analysis["face_detected"] = True
            analysis["face_count"] = len(faces)
            analysis["face_coords"] = faces

            # ANOMALY: Multiple people check
            if len(faces) > 1:
                analysis["anomaly"] = "Multiple faces detected"
            
            # EMOTION: Process the largest face
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = largest_face
            
            # Crop face for DeepFace
            face_img = frame[y:y+h, x:x+w]
            
            try:
                # 'analyze' with detector_backend='skip' assumes we already cropped the face
                predictions = DeepFace.analyze(
                    face_img, 
                    actions=['emotion'], 
                    enforce_detection=False, 
                    detector_backend='skip',
                    silent=True
                )
                
                top_emotion = predictions[0]['dominant_emotion']
                score = predictions[0]['emotion'][top_emotion]
                
                analysis["emotion"] = top_emotion
                analysis["emotion_score"] = round(score, 2)
            except Exception:
                pass 
        else:
            analysis["anomaly"] = "No face detected"

        return analysis

# ==========================================
# TEST CODE
# ==========================================
# if __name__ == "__main__":
#     print("Initializing Camera...")
    
#     # Try index 0 first, if that fails (e.g., if you have many virtual cams), try 1
#     cap = cv2.VideoCapture(0) 

#     if not cap.isOpened():
#         print("❌ Error: Could not open camera. Check if Zoom/Teams is using it.")
#         exit()

#     service = EmotionService()
#     print("📷 Camera Started. Press 'q' to quit.")

#     while True:
#         success, frame = cap.read()
#         if not success: break

#         # Analyze
#         data = service.analyze_frame(frame)
        
#         # Draw Results
#         for (x, y, w, h) in data["face_coords"]:
#             cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
#         status_text = f"Emotion: {data['emotion']} ({data['emotion_score']}%)"
#         if data['anomaly']:
#             status_text = f"ALERT: {data['anomaly']}"

#         cv2.putText(frame, status_text, (20, 50), 
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

#         cv2.imshow('AI Interviewer Monitor', frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()