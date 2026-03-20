import logging
import psycopg2
from db.config.config import DB_CONFIG, TABLE_NAME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_connection():
    """
    Establishes a connection to the PostgreSQL database

    :return: Connection | None
    """

    logger.info("Attempting to connect to the database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Successfully connected to the database.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None
        # TODO: Handle the exception -> retry logic, create the database if it doesn't exist, etc.