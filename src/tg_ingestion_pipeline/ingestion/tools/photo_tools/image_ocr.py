from typing import Optional, List 
import easyocr

def ocr(image_path) -> Optional[str]:
    """
    Perform OCR on the given image file.
    
    :param image_path: Path to the image file to be processed
    :return: List of extracted text lines or None if processing fails
    :rtype: List[str] | None
    """


    try: 
        reader = easyocr.Reader(['en'], gpu=False, verbose=True)
        results = reader.readtext(image_path)
        text: List[str] = [r[1] for r in results]
        return "\n".join(text)
    except Exception as e:
        print(f"Processing image failed: {e}")
        return None