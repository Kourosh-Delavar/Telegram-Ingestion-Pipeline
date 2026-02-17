import logging
from typing import Any, Dict, Optional
from telegram import Update
from telegram.ext import ContextTypes
from utils.base_msg import extract_base_message_data 


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[Dict[str, Any]]:
    """
    Handle document messages.
    
    args:
        update: Telegram Update object
        context: Telegram Context object
    """
    try:
        msg = update.message
        if not msg or not msg.document:
            logger.warning("Received document message without content")
            return None

        data = {
            "type": "document",
            "content": msg.document.file_id,
            "file_name": msg.document.file_name,
            "mime_type": msg.document.mime_type,
            **extract_base_message_data(msg),
        }
        logger.info(f"Document message received from {msg.from_user.username}")
        return data
    except Exception as e:
        logger.error(f"Error handling document message: {e}")
        return None