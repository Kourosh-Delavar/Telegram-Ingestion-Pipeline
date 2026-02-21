import logging
from pathlib import Path
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from .utils.base_msg import extract_base_message_data
from .utils.mime_type_converter import mime_type_to_extension
from loading.save_media_files import save_media_files 


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

        data = {
            "type": "photo",
            "content": [photo.file_id for photo in msg.photo],
            **extract_base_message_data(msg),
        }
        logger.info(f"Photo message received from {msg.from_user.username}")
        
        # Save the photo file
        await save_media_files(update, context)
        
        return data
    except Exception as e:
        logger.error(f"Error handling photo message: {e}")
        return None