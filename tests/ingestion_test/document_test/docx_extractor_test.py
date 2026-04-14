import pytest
from pathlib import Path
from tg_ingestion_pipeline.ingestion.tools.document_tools.docx_extractor import extract_text_from_docx


def test_extract_text_from_docx_file(tmp_path):
    pytest.importorskip("docx")
    from docx import Document

    doc_path = tmp_path / "sample.docx"
    doc = Document()
    doc.add_paragraph("Hello from docx")
    doc.save(doc_path)

    extracted = extract_text_from_docx(doc_path)
    assert extracted == "Hello from docx"
