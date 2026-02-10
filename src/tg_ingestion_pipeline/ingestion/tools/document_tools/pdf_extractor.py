from typing import Optional
import pdfplumber as pdfPlumber


def extract_text_from_pdf(file_path) -> Optional[str]:
    try:
        with pdfPlumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            cleaned = text.strip()
            return cleaned if cleaned else None
    except Exception as e:
        print(f"\nFailed to extract text from pdf file {file_path}: {e}")
        return None
