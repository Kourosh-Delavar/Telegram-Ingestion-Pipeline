from typing import Optional
from docx import Document

def extract_text_from_docx(file_path) -> Optional[str]:
    """
    Extract text from a Microsoft Word (.docx) file.
    
    :param file_path: Path to the .docx file to be processed
    :return: The extracted text or None if processing fails
    :rtype: str | None
    """

    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"Failed to extract text from docx file {file_path}: {e}")
        return None