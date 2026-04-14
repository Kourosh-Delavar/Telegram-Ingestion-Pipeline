import importlib
import sys
from types import SimpleNamespace


def test_sst_transcribe_handles_failure(monkeypatch):
    class DummyWhisper:
        @staticmethod
        def is_cuda_available():
            return False

        @staticmethod
        def load_model(name, device=None):
            class DummyModel:
                def transcribe(self, audio_path, fp16=False):
                    raise FileNotFoundError("audio model missing")

            return DummyModel()

    monkeypatch.setitem(sys.modules, "whisper", DummyWhisper)
    module_name = "tg_ingestion_pipeline.ingestion.tools.audio_tools.sst"
    if module_name in sys.modules:
        del sys.modules[module_name]

    sst_module = importlib.import_module(module_name)
    assert sst_module.transcribe("missing_file.mp3") is None