from typing import Optional
import whisper

def transcribe(audio_path) -> Optional[str]:
    try:
        model = whisper.load_model("base", device="cpu") # TODO: Make it generic for both cpu and gpu
        result = model.transcribe(audio_path, fp16=False)
        return result["text"]
    except Exception as e:
        print(f"Transcription failed: {e}")
        return None