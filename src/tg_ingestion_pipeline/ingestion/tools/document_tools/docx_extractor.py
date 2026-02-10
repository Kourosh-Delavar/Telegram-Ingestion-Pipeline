from typing import Optional
from docx import Document

def extract_text_from_docx(file_path) -> Optional[str]:
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"Failed to extract text from docx file {file_path}: {e}")
        return None