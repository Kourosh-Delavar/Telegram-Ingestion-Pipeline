from typing import Optional
import whisper

def transcribe(audio_path) -> Optional[str]:
    """
    transcribe the given audio file using OpenAI's Whisper model.
    
    :param audio_path: Path to the audio file to be transcribed
    :type audio_path: str | Path
    :return: The transcribed text or None if transcription fails
    :rtype: str | None
    """

    try:
        device = "cuda" if whisper.is_cuda_available() else "cpu"
        model = whisper.load_model("base", device=device) 
        result = model.transcribe(audio_path, fp16=False)
        return result["text"]
    except Exception as e:
        print(f"Transcription failed: {e}")
        return None