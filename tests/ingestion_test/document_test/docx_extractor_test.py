from typing import Optional, List
from tg_ingestion_pipeline.ingestion.tools.document_tools.docx_extractor import extract_text_from_docx
from pathlib import Path

def test_docx_extractor(paths: List[str]) -> None:
    for path in paths:
        text = extract_text_from_docx(path)
        if text is not None:
            print(f"\nText extracted successfully from {path}:\n{text}\n")
        else:
            print(f"\nFailed to extract text from {path}")

base_dir = Path(__file__).resolve().parent.parent.parent
document_dir = base_dir / "resources" / "document"
paths: List[str] = [str(d) for d in document_dir.glob("*.docx")]
if paths:
    print(f"\nFound {len(paths)} DOCX files to process.")
else:
    print("\nNo DOCX files found to process.")

test_docx_extractor(paths)