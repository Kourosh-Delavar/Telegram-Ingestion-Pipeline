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
from handlers import (
    handle_message,
    handle_photo,
    handle_document,
    handle_audio,
)
from tg_ingestion_pipeline.loading.save_media_files import save_media_files

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
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    # Add handler for saving messages containing media files to the data/ directory
    app.add_handler(MessageHandler(filter.PHOTO 
                                   | filters.Document.ALL  
                                   | filters.AUDIO 
                                   | filters.VOICE,
                                     save_media_files))

def main() -> None:
    """
    Main entry point for the bot.

    :return: None
    """

    logger.info("Starting Telegram ingestion bot")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    setup_handlers(app)

    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")


if __name__ == "__main__":
    main()