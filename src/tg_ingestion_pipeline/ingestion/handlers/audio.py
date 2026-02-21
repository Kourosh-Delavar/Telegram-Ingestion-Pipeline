import logging
from pathlib import Path
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from .utils.base_msg import extract_base_message_data
from .utils.mime_type_converter import mime_type_to_extension
from ingestion.tools.audio_tools.sst import transcribe
import json
from kafka.kafka_engine import KafkaOrchestrator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

        # Data directory for saving audio files
        base_dir = Path(__file__).parent.parent.parent.parent
        music_dir = base_dir / "data" / "audio" / "music"
        voice_dir = base_dir / "data" / "audio" / "voice"

        # Finding subdirectory based on audio type
        if msg.audio.mime_type and "music" in msg.audio.mime_type:
            data_dir = music_dir
        elif msg.audio.mime_type and "voice" in msg.audio.mime_type:
            data_dir = voice_dir
        else:
            logger.warning(f"Unknown audio type for mime_type: {msg.audio.mime_type}")
            data_dir = music_dir  # Default to music directory
        
        # Transcribe the audio file 
        try:
            file_extension = mime_type_to_extension(mime_type, media_type="audio")
            extracted_content: Optional[str] = await transcribe(data_dir / f"{file_id}.{file_extension}")
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
            logger.info(f"Audio message received from {msg.from_user.username} without transcription. Using file_id as content.")
        
        # Configure Kafka producer (running on localhost:9092 by default)
        cfg_path = Path(__file__).parent.parent.parent.parent / "kafka" / "configs" / "clients.json"
        conf = json.load(open(cfg_path))["audio_handler"]
        
        kafka = KafkaOrchestrator(conf)
        kafka.send_message(
            topic = "extracted-data",
            key = file_id,
            data = data
        )
    except Exception as e:
        logger.error(f"Error handling audio message: {e}")
        return None