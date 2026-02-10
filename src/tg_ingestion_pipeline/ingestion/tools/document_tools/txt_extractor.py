from typing import Optional

def extract_text_from_txt_file(file_path) -> Optional[str]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            return text
    except Exception as e:
        print(f"Failed to extract text from txt file: {e}")
        return None