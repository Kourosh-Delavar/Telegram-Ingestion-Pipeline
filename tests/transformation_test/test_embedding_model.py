import sys
import types
from tg_ingestion_pipeline.transformation.embeddings.embedding_model import Vectorizer


def test_vectorizer_uses_sentence_transformer(monkeypatch):
    class DummyModel:
        def __init__(self, model_name):
            self.model_name = model_name

        def get_sentence_embedding_dimension(self):
            return 3

        def encode(self, text, convert_to_list=True):
            return [float(len(text)), 0.5, 0.25]

    dummy_module = types.SimpleNamespace(SentenceTransformer=DummyModel)
    monkeypatch.setitem(sys.modules, "sentence_transformers", dummy_module)

    vectorizer = Vectorizer(model_name="dummy-model")

    assert vectorizer.model is not None
    embedding = vectorizer.vectorize({
        "content": "hello world",
        "message_type": "text",
        "username": "tester",
        "file_name": "hello.txt",
        "mime_type": "text/plain",
    })

    assert embedding == [float(len("hello world\n\nMetadata: Type: text | User: tester | File: hello.txt | MIME: text/plain")), 0.5, 0.25]


def test_vectorizer_empty_payload_returns_zero_vector(monkeypatch):
    class DummyModel:
        def __init__(self, model_name):
            self.model_name = model_name

        def get_sentence_embedding_dimension(self):
            return 4

        def encode(self, text, convert_to_list=True):
            return [1.0, 2.0, 3.0, 4.0]

    dummy_module = types.SimpleNamespace(SentenceTransformer=DummyModel)
    monkeypatch.setitem(sys.modules, "sentence_transformers", dummy_module)

    vectorizer = Vectorizer(model_name="dummy-model")

    assert vectorizer.vectorize({}) == [0.0, 0.0, 0.0, 0.0]
