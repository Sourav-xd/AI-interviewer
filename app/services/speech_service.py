# app/services/speech_service.py
import os
import asyncio
import edge_tts
from faster_whisper import WhisperModel

# Fix for some Windows environments where multiple OpenMP libraries conflict
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class SpeechService:
    def __init__(self):
        print("🎙️ Loading Speech AI Models... (One-time setup)")
        
        # 1. LOAD WHISPER (STT)
        # 'tiny.en' is the fastest model for English. 
        # If you want more accuracy (but slower), change to 'base.en' or 'small.en'.
        # device="cpu" with compute_type="int8" is the standard for fast CPU inference.
        try:
            self.stt_model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
            print("✅ Whisper (STT) Loaded.")
        except Exception as e:
            print(f"❌ Error loading Whisper: {e}")
            self.stt_model = None
            
        # 2. CONFIGURE VOICE (TTS)
        # "en-US-ChristopherNeural" is a professional male interviewer voice.
        # "en-US-AriaNeural" is a professional female interviewer voice.
        self.voice = "en-US-ChristopherNeural"

    def speech_to_text(self, audio_file_path: str) -> str:
        """
        Converts an audio file (mp3/wav/webm) to text.
        """
        if not self.stt_model: 
            return "Error: Model not loaded."
        
        try:
            # beam_size=1 is faster (greedy search), acceptable for live chat
            segments, info = self.stt_model.transcribe(
                audio_file_path, 
                beam_size=1, 
                language="en",
                vad_filter=True # Filters out silence/background noise
            )
            
            # Combine all segments into one string
            text = " ".join([segment.text for segment in segments])
            return text.strip()
        except Exception as e:
            print(f"STT Conversion Error: {e}")
            return ""

    async def text_to_speech(self, text: str, output_file: str) -> str:
        """
        Converts text to an MP3 file using Microsoft Edge's high-quality voices.
        """
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(output_file)
            return output_file
        except Exception as e:
            print(f"TTS Generation Error: {e}")
            return None

# ==========================================
# SELF-TEST CODE (No Mic Needed)
# ==========================================
# if __name__ == "__main__":
#     # We will test the pipeline by:
#     # 1. Generating audio from text (TTS)
#     # 2. Converting that audio back to text (STT)
#     # This verifies both systems work without needing a microphone in Python.
    
#     async def run_latency_test():
#         print("\n--- Starting Speech Service Test ---")
#         service = SpeechService()
        
#         test_filename = "test_interview_audio.mp3"
#         test_phrase = "Hello candidate, let us begin the interview."

#         # TEST 1: Text-to-Speech
#         print(f"\n[1/2] Generating Voice for: '{test_phrase}'...")
#         await service.text_to_speech(test_phrase, test_filename)
        
#         if os.path.exists(test_filename):
#             print(f" TTS Success! Audio saved to '{test_filename}'")
#         else:
#             print(" TTS Failed.")
#             return

#         # TEST 2: Speech-to-Text
#         print(f"\n[2/2] Transcribing '{test_filename}' back to text...")
#         transcription = service.speech_to_text(test_filename)
        
#         print(f"Original:      {test_phrase}")
#         print(f"Transcribed:   {transcription}")
        
#         if "begin" in transcription.lower() or "hello" in transcription.lower():
#             print("\n✅ SUCCESS: Full cycle (Text -> Audio -> Text) is working!")
#         else:
#             print("\n⚠️ WARNING: Transcription quality was low.")

#         # Cleanup
#         #try:
#         #    os.remove(test_filename)
#         #except:
#         #    pass

#     asyncio.run(run_latency_test())