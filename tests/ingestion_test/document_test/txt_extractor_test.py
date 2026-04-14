from pathlib import Path
from tg_ingestion_pipeline.ingestion.tools.document_tools.txt_extractor import extract_text_from_txt_file


def test_extract_text_from_txt_file(tmp_path):
    sample_text = "This is a text extractor test."
    text_file = tmp_path / "sample.txt"
    text_file.write_text(sample_text, encoding="utf-8")

    extracted = extract_text_from_txt_file(text_file)
    assert extracted == sample_text