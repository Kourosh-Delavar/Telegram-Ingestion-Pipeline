import logging
from typing import Dict, Any
from pathlib import Path
from .utils.get_query import get_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[3]
INSERT_SQL_PATH = BASE_DIR / "db" / "postgres" / "utils" / "001_insert_data.sql"

def insert_message(conn, message: Dict[str, Any]) -> bool:
    """
    Insert a single Telegram message record into the relational database.

    :param conn: Connection object
    :param message: message payload dictionary
    :return: bool
    """

    try:
        query = get_query(str(INSERT_SQL_PATH))
        logger.info("Inserting message into the relational database...")
        with conn.cursor() as curs:
            curs.execute(query, message)
        conn.commit()
        logger.info("Message persisted to the relational database.")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting message: {e}")
        return False
    finally:
        conn.close()
 