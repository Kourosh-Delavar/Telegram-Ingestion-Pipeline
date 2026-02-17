from typing import Optional

def extract_text_from_txt_file(file_path) -> Optional[str]:
    """
    Extract text from a plain text (.txt) file.
    
    :param file_path: Path to the .txt file to be processed
    :return: The extracted text or None if processing fails
    :rtype: str | None
    """

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            return text
    except Exception as e:
        print(f"Failed to extract text from txt file: {e}")
        return None