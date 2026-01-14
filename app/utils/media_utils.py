import base64
import numpy as np
import cv2
import uuid
import os

def decode_base64_image(base64_string: str):
    """
    Converts a base64 string (from frontend video frame) to an OpenCV image.
    """
    try:
        # Remove header if present (e.g., "data:image/jpeg;base64,")
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
            
        image_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        print(f"Image Decode Error: {e}")
        return None

def save_base64_audio(base64_string: str) -> str:
    """
    Decodes base64 audio and saves to a temp file. Returns the file path.
    """
    try:
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
            
        audio_data = base64.b64decode(base64_string)
        
        # Create a unique temp filename
        filename = f"temp_{uuid.uuid4()}.webm"
        
        with open(filename, "wb") as f:
            f.write(audio_data)
            
        return filename
    except Exception as e:
        print(f"Audio Save Error: {e}")
        return None