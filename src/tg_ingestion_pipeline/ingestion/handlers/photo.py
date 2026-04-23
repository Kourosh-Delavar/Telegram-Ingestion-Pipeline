import logging
from telegram import Update
from telegram.ext import ContextTypes
from .utils.base_msg import extract_base_message_data
from .utils.file_cleaner import delete_media_file
from tg_ingestion_pipeline.ingestion.tools.photo_tools.image_ocr import ocr
from tg_ingestion_pipeline.ingestion.services.media_downloader import download_photo
from tg_ingestion_pipeline.ingestion.services.message_publisher import publish_extracted_message


logger = logging.getLogger(__name__)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle photo messages.
    
    :param update: Telegram Update object
    :type update: Update
    :param context: Telegram Context object
    :type context: ContextTypes.DEFAULT_TYPE
    :return: None
    """

    try:
        msg = update.message
        if not msg or not msg.photo:
            logger.warning("Received photo message without content")
            return None

        # Use the largest photo (last in the list)
        photo = msg.photo[-1]
        file_id: str = photo.file_id
        logger.info(f"Photo file_id: {file_id}")
        # Download and OCR the photo in the same handler to avoid cross-handler races.
        file_path = None
        try:
            file_path = await download_photo(context, file_id=file_id)
            extracted_content = ocr(str(file_path))
        except Exception as e:
            logger.error(f"Error during photo OCR: {e}")
            extracted_content = None

        text_content = extracted_content if extracted_content is not None else ""

        if extracted_content is not None:
            data = {
                "file_id": file_id,
                "type": "photo",
                "content": text_content,
                **extract_base_message_data(msg),
            }
            logger.info(f"Photo message received from {msg.from_user.username}")
        else:
            data = {
                "file_id": file_id,
                "type": "photo",
                "content": file_id,
                **extract_base_message_data(msg),
            }
            logger.info(f"Photo message received from {msg.from_user.username} without extracted content. Using file_id as content.")

        publish_extracted_message(key=file_id, data=data)
        
        # Delete media file after successful extraction and Kafka message sending
        if file_path is not None:
            delete_media_file(file_path)
    except Exception as e:
        logger.error(f"Error handling photo message: {e}")
        return None