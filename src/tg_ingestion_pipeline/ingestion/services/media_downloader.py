from pathlib import Path

from telegram.ext import ContextTypes

from tg_ingestion_pipeline.ingestion.handlers.utils.mime_type_converter import mime_type_to_extension


BASE_MEDIA_DIR = Path(__file__).resolve().parents[4] / "data" / "tg_files"


async def download_photo(context: ContextTypes.DEFAULT_TYPE, file_id: str) -> Path:
    file = await context.bot.get_file(file_id)
    extension = mime_type_to_extension("image/jpeg", media_type="photo")
    target_dir = BASE_MEDIA_DIR / "photos"
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / f"{file_id}.{extension}"
    file_bytes = await file.download_as_bytearray()
    file_path.write_bytes(file_bytes)
    return file_path


async def download_document(context: ContextTypes.DEFAULT_TYPE, file_id: str, mime_type: str | None) -> Path:
    file = await context.bot.get_file(file_id)
    extension = mime_type_to_extension(mime_type, media_type="document")
    if extension == "pdf":
        sub_dir = "pdf"
    elif extension in {"docx", "doc"}:
        sub_dir = "docx"
    else:
        sub_dir = "txt"

    target_dir = BASE_MEDIA_DIR / "documents" / sub_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / f"{file_id}.{extension}"
    file_bytes = await file.download_as_bytearray()
    file_path.write_bytes(file_bytes)
    return file_path


async def download_audio(context: ContextTypes.DEFAULT_TYPE, file_id: str, mime_type: str | None) -> Path:
    file = await context.bot.get_file(file_id)
    extension = mime_type_to_extension(mime_type, media_type="audio")
    sub_dir = "voice" if extension == "ogg" else "music"
    target_dir = BASE_MEDIA_DIR / "audios" / sub_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    file_path = target_dir / f"{file_id}.{extension}"
    file_bytes = await file.download_as_bytearray()
    file_path.write_bytes(file_bytes)
    return file_path
