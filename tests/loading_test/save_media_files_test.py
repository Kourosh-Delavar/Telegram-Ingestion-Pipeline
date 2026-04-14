import asyncio
from pathlib import Path
from tg_ingestion_pipeline.loading.saving.save_media_files import save_media_files


class DummyFile:
    def __init__(self, data: bytes):
        self._data = data

    async def download_as_bytearray(self):
        return self._data


class DummyBot:
    def __init__(self, file_obj):
        self._file_obj = file_obj

    async def get_file(self, file_id):
        return self._file_obj


class DummyContext:
    def __init__(self, bot):
        self.bot = bot


class DummyPhoto:
    def __init__(self, file_id):
        self.file_id = file_id


class DummyDocument:
    def __init__(self, file_id, mime_type):
        self.file_id = file_id
        self.mime_type = mime_type


class DummyMessage:
    def __init__(self, photo=None, document=None, audio=None, voice=None):
        self.photo = photo
        self.document = document
        self.audio = audio
        self.voice = voice


class DummyUpdate:
    def __init__(self, message):
        self.message = message


def _cleanup(path: Path):
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


def test_save_media_files_downloads_photo():
    content = b"photo bytes"
    file_id = "photo_test_id"
    fake_file = DummyFile(content)
    context = DummyContext(DummyBot(fake_file))
    update = DummyUpdate(DummyMessage(photo=[DummyPhoto(file_id)]))

    target_path = Path(__file__).resolve().parents[2] / "data" / "tg_files" / "photos" / f"{file_id}.jpg"
    _cleanup(target_path)

    asyncio.run(save_media_files(update, context))

    assert target_path.exists()
    assert target_path.read_bytes() == content
    _cleanup(target_path)


def test_save_media_files_downloads_pdf_document():
    content = b"pdf bytes"
    file_id = "pdf_test_id"
    fake_file = DummyFile(content)
    context = DummyContext(DummyBot(fake_file))
    document = DummyDocument(file_id=file_id, mime_type="application/pdf")
    update = DummyUpdate(DummyMessage(photo=None, document=document))

    target_path = Path(__file__).resolve().parents[2] / "data" / "tg_files" / "documents" / "pdf" / f"{file_id}.pdf"
    _cleanup(target_path)

    asyncio.run(save_media_files(update, context))

    assert target_path.exists()
    assert target_path.read_bytes() == content
    _cleanup(target_path)


def test_save_media_files_handles_missing_message():
    context = DummyContext(DummyBot(DummyFile(b"")))
    update = DummyUpdate(message=None)

    assert asyncio.run(save_media_files(update, context)) is None
