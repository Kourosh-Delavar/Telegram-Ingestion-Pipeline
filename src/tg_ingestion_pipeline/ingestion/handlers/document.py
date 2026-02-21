import logging
from pathlib import Path
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from .utils.base_msg import extract_base_message_data
from .utils.mime_type_converter import mime_type_to_extension
from ingestion.tools.document_tools import (
    pdf_extractor,
    docx_extractor,
    txt_extractor
)
import json
from kafka.kafka_engine import KafkaOrchestrator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle document messages.
    
    :param update: Telegram Update object
    :type update: Update
    :param context: Telegram Context object
    :type context: ContextTypes.DEFAULT_TYPE
    :return: None
    """


    try:
        msg = update.message
        if not msg or not msg.document:
            logger.warning("Received document message without content")
            return None
        
        file_id: str = msg.document.file_id
        logger.info(f"Document file_id: {file_id}")
        mime_type: Optional[str] = msg.document.mime_type.lower() if msg.document.mime_type else None
        logger.info(f"Document mime_type: {mime_type}")

        # Data directory for saving document files
        base_dir = Path(__file__).parent.parent.parent.parent
        pdf_dir = base_dir / "data" / "document" / "pdf"
        docx_dir = base_dir / "data" / "document" / "docx"
        txt_dir = base_dir / "data" / "document" / "txt"

        # Finding subdirectory based on document type
        file_extension = mime_type_to_extension(mime_type, media_type="document")
        
        extension_to_dir = {
            "pdf": pdf_dir,
            "docx": docx_dir,
            "doc": docx_dir,
            "txt": txt_dir,
            "html": txt_dir,
            "rtf": txt_dir,
        }
        
        target_dir = extension_to_dir.get(file_extension, txt_dir) 

        data = {
            "type": "document",
            "content": msg.document.file_id,
            "file_name": msg.document.file_name,
            "mime_type": msg.document.mime_type,
            **extract_base_message_data(msg),
        }
        logger.info(f"Document message received from {msg.from_user.username}")
        
    except Exception as e:
        logger.error(f"Error handling document message: {e}")
        return None