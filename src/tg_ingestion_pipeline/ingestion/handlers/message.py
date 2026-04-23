import logging
from telegram import Update
from telegram.ext import ContextTypes
from .utils.base_msg import extract_base_message_data 
from tg_ingestion_pipeline.ingestion.services.message_publisher import publish_extracted_message

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle text messages.
    
    :param update: Telegram Update object
    :type update: Update
    :param context: Telegram Context object
    :type context: ContextTypes.DEFAULT_TYPE
    :return: None
    """
    
    try:
        msg = update.message
        if not msg or not msg.text:
            logger.warning("Received text message without content")
            return None

        msg_id = msg.message_id

        data = {
            "type": "text",
            "content": msg.text,
            **extract_base_message_data(msg),
        }
        logger.info(f"Text message received from {msg.from_user.username}")
        
        publish_extracted_message(key=str(msg_id), data=data)
    except Exception as e:
        logger.error(f"Error handling text message: {e}")
        return None