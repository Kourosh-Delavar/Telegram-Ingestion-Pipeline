import logging
import os
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from handlers.message import handle_message
from handlers.photo import handle_photo
from handlers.document import handle_document
from handlers.audio import handle_audio
from loading.save_media_files import save_media_files

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set.")


def setup_handlers(app) -> None:
    """
    Register message handlers.
    
    :param app: Telegram Application object
    :type app: Application
    """
    
    logger.info("Setting up handlers...")
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Added TEXT handler")
    
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    logger.info("Added PHOTO handler (primary)")
    
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    logger.info("Added DOCUMENT handler (primary)")
    
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    logger.info("Added AUDIO handler (primary)")
    
    # Add handler for saving messages containing media files to the data/ directory
    logger.info(f"Adding save_media_files handler with filters: PHOTO | Document.ALL | AUDIO | VOICE")
    app.add_handler(MessageHandler(filters.PHOTO 
                                   | filters.Document.ALL  
                                   | filters.AUDIO 
                                   | filters.VOICE,
                                     save_media_files))
    logger.info("Added save_media_files handler (secondary)")
    logger.info("All handlers registered successfully")

def main() -> None:
    """
    Main entry point for the bot.

    :return: None
    """

    logger.info("Starting Telegram ingestion bot")
    logger.info(f"save_media_files function: {save_media_files}")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    logger.info("Application built successfully")
    
    setup_handlers(app)
    logger.info("Handlers setup completed")

    try:
        logger.info("Starting polling...")
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")


if __name__ == "__main__":
    main()