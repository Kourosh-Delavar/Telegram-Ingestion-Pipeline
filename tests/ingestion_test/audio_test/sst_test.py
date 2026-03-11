from typing import List
from tg_ingestion_pipeline.ingestion.tools.audio_tools.sst import transcribe
from pathlib import Path

def transcribe_test(path_list: List[str]) -> None:
    for path in path_list:
        result = transcribe(path)
        if result is not None:
            print(f"\nTranscription successful for {path}:\n{result}\n")
        else: 
            print(f"\nTranscription failed for {path}")

base_dir = Path(__file__).resolve().parent.parent.parent
audio_dir = base_dir / "resources" / "audio"
path_list = [str(p) for p in audio_dir.glob("*.mp3")] + \
            [str(p) for p in audio_dir.glob("*.wav")] + \
            [str(p) for p in audio_dir.glob("*.ogg")]
if path_list:
    print(f"\nFound {len(path_list)} audio files to process.")
else: 
    print("\nNo audio files found to process.")

transcribe_test(path_list)