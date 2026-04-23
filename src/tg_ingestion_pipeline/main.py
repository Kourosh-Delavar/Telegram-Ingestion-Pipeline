import logging
import os
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
)
from tg_ingestion_pipeline.ingestion.handlers.message import handle_message             
from tg_ingestion_pipeline.ingestion.handlers.photo import handle_photo                 
from tg_ingestion_pipeline.ingestion.handlers.document import handle_document           
from tg_ingestion_pipeline.ingestion.handlers.audio import handle_audio                 
from tg_ingestion_pipeline.loading.saving.save_media_files import save_media_files
from tg_ingestion_pipeline.loading.db.connect_db import get_connection 
from tg_ingestion_pipeline.loading.db.init_db import initialize_db
from tg_ingestion_pipeline.transformation.processing.pipeline import TelegramDataPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv(".env.token") # TODO: Make the path to .env file configurable via environment variable or command-line argument

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set.")


def setup_handlers(app) -> None:
    """
    Register message handlers.
    
    :param app: Telegram Application object
    :type app: Application
    :return: None
    """
    
    logger.info("Registering the message handlers...")
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Add TEXT handler")
    
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    logger.info("Add PHOTO handler (primary)")
    
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    logger.info("Add DOCUMENT handler (primary)")
    
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    logger.info("Add AUDIO handler (primary)")
    
    # Add handler for saving messages containing media files to the data/ directory
    app.add_handler(MessageHandler(filters.PHOTO 
                                   | filters.Document.ALL  
                                   | filters.AUDIO 
                                   | filters.VOICE,
                                     save_media_files))
    logger.info(f"Add save_media_files handler with filters: PHOTO | Document.ALL | AUDIO | VOICE")
    
    logger.info("All handlers registered successfully")

def main() -> None:
    
    logger.info("Starting Telegram ingestion bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Try to connect to database, but allow bot to run without it (for testing)
    conn = get_connection()
    if conn is None:
        logger.warning('Unable to connect to PostgreSQL. The bot will run without database support.')
        logger.warning('Make sure Docker containers are running: docker-compose up -d')
    else:
        try:
            initialize_db(conn=conn)
            logger.info('Database initialized successfully')
        except Exception as e:
            logger.error(f"Error initializing database: {e}")

    # Start background pipeline if database is available
    try:
        pipeline = TelegramDataPipeline()
        pipeline.start_async()
        logger.info('Background data pipeline started')
    except Exception as e:
        logger.warning(f'Could not start background pipeline: {e}')
        logger.warning('Pipeline requires database connection')

    logger.info("Application built successfully")
    
    setup_handlers(app)
    logger.info("Handlers setup completed")

    try:
        logger.info("Start polling...")
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")

if __name__ == "__main__":
    main()