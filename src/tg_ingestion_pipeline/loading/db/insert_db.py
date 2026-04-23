import logging
from functools import lru_cache
from typing import Dict, Any
from pathlib import Path
from .utils.get_query import get_query

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
        query = _insert_query()
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


@lru_cache(maxsize=1)
def _insert_query() -> str:
    query = get_query(str(INSERT_SQL_PATH))
    if not query:
        raise RuntimeError(f"Failed to load SQL query from {INSERT_SQL_PATH}")
    return query
 