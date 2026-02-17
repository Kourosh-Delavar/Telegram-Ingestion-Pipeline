from typing import Dict
from pathlib import Path 

def load_paths() -> Dict[str, Path]:
    BASE_DIR = Path(__file__).parent.parent.parent.parent / "data"
    paths = {
        "photos": BASE_DIR / "tg_files/photos",
        "documents": BASE_DIR / "tg_files/documents",
        "audio": BASE_DIR / "tg_files/audio",
    }
    return paths