import logging
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from .utils.base_msg import extract_base_message_data
from .utils.file_cleaner import delete_media_file
from tg_ingestion_pipeline.ingestion.tools.audio_tools.sst import transcribe
from tg_ingestion_pipeline.ingestion.services.media_downloader import download_audio
from tg_ingestion_pipeline.ingestion.services.message_publisher import publish_extracted_message


logger = logging.getLogger(__name__)


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle audio messages.
    
    :param update: Telegram Update object
    :type update: Update
    :param context: Telegram Context object
    :type context: ContextTypes.DEFAULT_TYPE
    :return: None
    """


    try:
        msg = update.message
        if not msg or not msg.audio:
            logger.warning("Received audio message without content")
            return None

        file_id: str = msg.audio.file_id
        logger.info(f"Audio file_id: {file_id}")
        mime_type: Optional[str] = msg.audio.mime_type.lower() if msg.audio.mime_type else None
        logger.info(f"Audio mime_type: {mime_type}")

        # Download and transcribe in the same handler to avoid race conditions.
        file_path = None
        try:
            file_path = await download_audio(context, file_id=file_id, mime_type=mime_type)
            extracted_content = transcribe(file_path)
        except Exception as e:
            logger.error(f"Error during audio transcription: {e}")
            extracted_content = None

        # Create the data dictionary using the extracted content if available, otherwise fallback to file_id
        if extracted_content is not None:
            data = {
                "file_id": file_id,
                "type": "audio",
                "content": extracted_content,
                "duration": msg.audio.duration,
                "mime_type": msg.audio.mime_type,
                **extract_base_message_data(msg),
            }
            logger.info(f"Audio message received from {msg.from_user.username}")
        else:
            data = {
                "file_id": file_id,
                "type": "audio",
                "content": file_id,
                "duration": msg.audio.duration,
                "mime_type": msg.audio.mime_type,
                **extract_base_message_data(msg),
            }
            logger.info(f"Audio message received from {msg.from_user.username} without extracted content. Using file_id as content.")

        publish_extracted_message(key=file_id, data=data)
        
        # Delete media file after successful extraction and Kafka message sending
        if file_path is not None:
            delete_media_file(file_path)
    except Exception as e:
        logger.error(f"Error handling audio message: {e}")
        return None