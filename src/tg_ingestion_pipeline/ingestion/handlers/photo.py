import logging
from pathlib import Path
from typing import Optional, List
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from .utils.base_msg import extract_base_message_data
from .utils.mime_type_converter import mime_type_to_extension
from tg_ingestion_pipeline.ingestion.tools.photo_tools.image_ocr import ocr
import json
from kafka.kafka_engine import KafkaOrchestrator


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

# Use the largest photo (last in the list)
        photo = msg.photo[-1]
        file_id: str = photo.file_id
        logger.info(f"Photo file_id: {file_id}")
        mime_type: Optional[str] = photo.mime_type.lower() if photo.mime_type else None
        logger.info(f"Photo mime_type: {mime_type}")

        # Data directory for saving photo files
        base_dir = Path(__file__).parent.parent.parent.parent
        photo_dir = base_dir / "data" / "photos"

        # OCR the photo
        try:
            file_extension = mime_type_to_extension(mime_type, media_type="photo")
            file_path = photo_dir / f"{file_id}.{file_extension}"
            
            # Retry logic to wait for file download
            max_retries = 10
            retry_delay = 1  # initial delay in seconds
            extracted_content = None
            for attempt in range(max_retries):
                if file_path.exists():
                    extracted_content = ocr(str(file_path))
                    break
                else:
                    logger.warning(f"Photo file not found at {file_path}, attempt {attempt + 1}/{max_retries}. Retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # exponential backoff
            else:
                logger.error(f"Photo file not found after {max_retries} attempts at {file_path}")
                
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

        # Configure Kafka producer (running on localhost:9092 by default)
        cfg_path = Path(__file__).parent.parent.parent.parent / "kafka" / "configs" / "clients.json"
        conf = json.load(open(cfg_path))["photo_handler"]
        
        kafka = KafkaOrchestrator(conf)
        kafka.send_message(
            topic = "extracted-data",
            key = file_id,
            data = data
        )
    except Exception as e:
        logger.error(f"Error handling photo message: {e}")
        return None