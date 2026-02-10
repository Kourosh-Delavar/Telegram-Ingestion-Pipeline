from typing import Optional, List
from tg_ingestion_pipeline.ingestion.tools.document_tools.pdf_extractor import extract_text_from_pdf
from pathlib import Path

def test_pdf_extractor(paths: List[str]) -> None:
    for path in paths: 
        text = extract_text_from_pdf(path)
        if text is not None:
            print(f"\nText extracted successfully from {path}:\n{text}\n")
        else:
            print(f"\nFailed to extract text from {path}")

base_dir = Path(__file__).resolve().parent.parent.parent
document_dir = base_dir / "resources" / "document"
paths: List[str] = [str(d) for d in document_dir.glob("*.pdf")] 
if paths:
    print(f"\nFound {len(paths)} PDF files to process.")
else:
    print("\nNo PDF files found to process.")

test_pdf_extractor(paths)