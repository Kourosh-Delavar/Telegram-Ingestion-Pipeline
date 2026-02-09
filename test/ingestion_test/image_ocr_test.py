from typing import List
from tg_ingestion_pipeline.ingestion.tools import image_ocr
from pathlib import Path

def test_ocr(paths_list: List[str]) -> None:
    for path in paths_list:
        text = image_ocr.ocr(path)
        if text is not None:
            print(f"\nText extracted successfully from {path}:\n{text}\n")
        else:
            print(f"\nFailed to extract text from {path}")

base_dir = Path(__file__).resolve().parent.parent
photo_dir = base_dir / "resources" / "photo"
paths_list = [str(p) for p in photo_dir.glob("*.png")] + [str(p) for p in photo_dir.glob("*.jpg")]
if paths_list:
    print(f"\nFound {len(paths_list)} image files to process.")
else:
    print("\nNo image files found to process.")

test_ocr(paths_list)