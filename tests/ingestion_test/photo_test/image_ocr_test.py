import importlib
import sys
from types import SimpleNamespace


def test_image_ocr_handles_failure(monkeypatch):
    class DummyReader:
        @staticmethod
        def is_cuda_available():
            return False

        def __init__(self, langs, gpu, verbose):
            pass

        def readtext(self, image_path):
            raise FileNotFoundError("image missing")

    dummy_module = SimpleNamespace(Reader=DummyReader)
    monkeypatch.setitem(sys.modules, "easyocr", dummy_module)
    module_name = "tg_ingestion_pipeline.ingestion.tools.photo_tools.image_ocr"
    if module_name in sys.modules:
        del sys.modules[module_name]

    image_ocr = importlib.import_module(module_name)
    assert image_ocr.ocr("missing_image.png") is None