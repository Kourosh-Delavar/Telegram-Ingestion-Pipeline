from typing import Optional, List
from pathlib import Path

def test_txt_extractor(paths: List[str]) -> None:
    for path in paths:
        try:
            with open(path, 'r', encoding='utf-8') as file:
                text = file.read()
                print(f"\nText extracted successfully from {path}:\n{text}\n")
        except Exception as e:
            print(f"\nFailed to extract text from {path}. Error: {e}")

base_dir = Path(__file__).resolve().parent.parent.parent
document_dir = base_dir / "resources" / "document"
paths: List[str] = [str(d) for d in document_dir.glob("*.txt")]
if paths:
    print(f"\nFound {len(paths)} TXT files to process.")
else:
    print("\nNo TXT files found to process.")

test_txt_extractor(paths)