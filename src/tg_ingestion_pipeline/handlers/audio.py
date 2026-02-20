import logging
from typing import Any, Dict, Optional
from telegram import Update
from telegram.ext import ContextTypes
from .utils.base_msg import extract_base_message_data
from loading.save_media_files import save_media_files 


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[Dict[str, Any]]:
    """
    Handle audio messages.
    
    args:
        update: Telegram Update object
        context: Telegram Context object
    """
    try:
        msg = update.message
        if not msg or not msg.audio:
            logger.warning("Received audio message without content")
            return None

        data = {
            "type": "audio",
            "content": msg.audio.file_id,
            "duration": msg.audio.duration,
            "mime_type": msg.audio.mime_type,
            **extract_base_message_data(msg),
        }
        logger.info(f"Audio message received from {msg.from_user.username}")
        
        # Save the audio file
        await save_media_files(update, context)
        
        return data
    except Exception as e:
        logger.error(f"Error handling audio message: {e}")
        return None