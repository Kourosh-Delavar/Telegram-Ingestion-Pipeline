from pathlib import Path
from tg_ingestion_pipeline.ingestion.tools.document_tools.pdf_extractor import extract_text_from_pdf


def test_extract_text_from_pdf_sample():
    pdf_path = Path(__file__).resolve().parents[3] / "tests" / "resources" / "document" / "sample.pdf"
    assert pdf_path.exists()

    extracted_text = extract_text_from_pdf(pdf_path)
    assert extracted_text is not None
    assert len(extracted_text.strip()) > 0