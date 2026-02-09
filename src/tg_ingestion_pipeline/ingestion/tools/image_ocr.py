from typing import Optional, List 
import easyocr

def ocr(image_path) -> Optional[List[str]]:
    try: 
        reader = easyocr.Reader(['en'], gpu=False, verbose=True)
        results = reader.readtext(image_path)
        text: List[str] = [r[1] for r in results]
        return text 
    except Exception as e:
        print(f"Processing image failed: {e}")
        return None