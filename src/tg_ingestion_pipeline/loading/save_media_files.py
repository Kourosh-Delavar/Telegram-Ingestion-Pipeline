import logging
from typing import Optional, Dict
from telegram import Update, Message
from telegram.ext import ContextTypes
import json
import traceback
from pathlib import Path
import io

# Configure logging
logger = logging.getLogger(__name__)

# Log that the module was imported
logger.info(f"save_media_files module imported. Logger name: {__name__}")

async def save_media_files(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Save media files from a Telegram message to the data directory.
    
    :param update: The Telegram update object
    :type update: Update
    :param context: The Telegram context object
    :type context: ContextTypes.DEFAULT_TYPE
    """
    try:
        logger.info("=== save_media_files called ===")
        logger.info(f"Update object: {update}")
        logger.info(f"Update message: {update.message if update else 'No update'}")

        # Loading paths from JSON file
        try:
            # Get the directory where this script is located
            current_dir = Path(__file__).parent
            json_file = current_dir / "saving_paths.json"
            
            with open(json_file, "r") as f:
                    paths: Dict[str, str] = json.load(f)
            logger.info(f"Paths loaded successfully from {json_file}: {paths}")
        except FileNotFoundError as e:
            logger.error(f"Error: saving_paths.json not found at {json_file}. Exception: {e}")
            return
        except Exception as e:
            logger.error(f"Error loading paths JSON: {e}")
            return

        msg: Optional[Message] = update.message
        if not msg:
            logger.warning("No message object found in update")
            return
        
        logger.info(f"Message type - Photo: {bool(msg.photo)}, Document: {bool(msg.document)}, Audio: {bool(msg.audio)}, Voice: {bool(msg.voice)}")
        
        # Convert relative paths to absolute paths
        base_dir = Path(__file__).parent.parent.parent.parent
        data_dir = base_dir / "data" / "tg_files"
        data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Data directory: {data_dir}")
        
        # Check if the message contains a photo 
        if msg.photo:
            try:
                logger.info("Photo detected in message")
                # Save the photo file to the data directory
                file_id  = msg.photo[-1].file_id
                logger.info(f"Photo file_id: {file_id}")
                file  = await context.bot.get_file(file_id)
                logger.info(f"Photo file object obtained: {file}")
                extension = "jpg"
                logger.info(f"Photo extension: {extension}")
                photo_dir = data_dir / "photos"
                photo_dir.mkdir(parents=True, exist_ok=True)
                file_path = photo_dir / f"{file_id}.{extension}"
                logger.info(f"Starting download to: {file_path}")
                
                # Download file content and write directly
                file_bytes = await file.download_as_bytearray()
                with open(file_path, 'wb') as f:
                    f.write(file_bytes)
                
                logger.info(f"Photo downloaded successfully to {file_path}")
            except Exception as e:
                logger.error(f"Failed to download photo: {type(e).__name__}: {e}")
                logger.error(traceback.format_exc())

        # Check if the message contains a document (PDF, DOCX, TXT)
        elif msg.document:
            try:
                logger.info("Document detected in message")
                # Save the document file to the data directory
                file_id  = msg.document.file_id
                logger.info(f"Document file_id: {file_id}")
                file  = await context.bot.get_file(file_id)
                logger.info(f"Document file object obtained: {file}")
                
                # Determine document type and extension
                mime_type = msg.document.mime_type or "application/octet-stream"
                if "pdf" in mime_type:
                    doc_type = "pdf"
                elif "word" in mime_type or "docx" in mime_type:
                    doc_type = "docx"
                else:
                    doc_type = "txt"
                
                extension = doc_type
                logger.info(f"Document type: {doc_type}, extension: {extension}")
                
                doc_dir = data_dir / "documents" / doc_type
                doc_dir.mkdir(parents=True, exist_ok=True)
                file_path = doc_dir / f"{file_id}.{extension}"
                logger.info(f"Starting download to: {file_path}")
                
                # Download file content and write directly
                file_bytes = await file.download_as_bytearray()
                with open(file_path, 'wb') as f:
                    f.write(file_bytes)
                
                logger.info(f"Document downloaded successfully to {file_path}")
            except Exception as e:
                logger.error(f"Failed to download document: {type(e).__name__}: {e}")
                logger.error(traceback.format_exc())
        
        # Check if the message contains an audio file (music or voice message)
        elif msg.audio or msg.voice:
            try:
                logger.info("Audio file detected in message")
                # Save the audio file to the data directory
                file_id  = msg.audio.file_id if msg.audio else msg.voice.file_id
                logger.info(f"Audio file_id: {file_id}")
                file  = await context.bot.get_file(file_id)
                logger.info(f"Audio file object obtained: {file}")
                extension = (msg.audio.mime_type if msg.audio else msg.voice.mime_type).split("/")[-1].lower()
                logger.info(f"Audio extension: {extension}")
                
                if extension == "ogg":
                    subdir = "voice"
                else:
                    subdir = "music"
                logger.info(f"Audio type: {subdir}")
                
                audio_dir = data_dir / "audios" / subdir
                audio_dir.mkdir(parents=True, exist_ok=True)
                file_path = audio_dir / f"{file_id}.{extension}"
                logger.info(f"Starting download to: {file_path}")
                
                # Download file content and write directly
                file_bytes = await file.download_as_bytearray()
                with open(file_path, 'wb') as f:
                    f.write(file_bytes)
                
                logger.info(f"Audio file ({subdir}) downloaded successfully to {file_path}")
            except Exception as e:
                logger.error(f"Failed to download audio: {type(e).__name__}: {e}")
                logger.error(traceback.format_exc())
        else:
            logger.warning("Message received but contains no supported media (photo, document, or audio)")
            
    except Exception as e:
        logger.critical(f"CRITICAL ERROR in save_media_files: {type(e).__name__}: {e}")
        logger.critical(traceback.format_exc())  