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
        if "pdf" in file_extension:
            data_dir = pdf_dir
        elif "docx" in file_extension:
            data_dir = docx_dir
        elif "txt" in file_extension:
            data_dir = txt_dir
        else:
            logger.warning(f"Unknown document type for mime_type: {msg.document.mime_type}")
            data_dir = txt_dir

        # Scan the document
        try:
            if "pdf" in file_extension:
                extracted_content: Optional[str] = await pdf_extractor(data_dir / f"{file_id}.{file_extension}")
            elif "docx" in file_extension:
                extracted_content: Optional[str] = await docx_extractor(data_dir / f"{file_id}.{file_extension}")            
            elif "txt" in file_extension:
                extracted_content: Optional[str] = await txt_extractor(data_dir / f"{file_id}.{file_extension}")
        except Exception as e:
            logger.error(f"Error during document scanning: {e}")
            extracted_content = None

        if extracted_content is not None:
            data = {
                "file_id": file_id,
                "type": "document",
                "content": extracted_content,
                "file_name": msg.document.file_name,
                "mime_type": msg.document.mime_type,
                **extract_base_message_data(msg),
            }
            logger.info(f"Document message received from {msg.from_user.username}")
        else:
            data = {
                "file_id": file_id,
                "type": "document",
                "content": file_id,
                "file_name": msg.document.file_name,
                "mime_type": msg.document.mime_type,
                **extract_base_message_data(msg),
            }
            logger.info(f"Audio message received from {msg.from_user.username} without transcription. Using file_id as content.")

        # Configure Kafka producer (running on localhost:9092 by default)
        cfg_path = Path(__file__).parent.parent.parent.parent / "kafka" / "configs" / "clients.json"
        conf = json.load(open(cfg_path))["document_handler"]
        
        kafka = KafkaOrchestrator(conf)
        kafka.send_message(
            topic = "extracted-data",
            key = file_id,
            data = data
        )

    except Exception as e:
        logger.error(f"Error handling document message: {e}")
        return None