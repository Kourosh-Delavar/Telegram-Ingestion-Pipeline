import logging
from typing import Optional
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_batch
from pathlib import Path
from connect_db import get_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Path to SQL file used for initializing the database 
SQL_PATH = "./db/postgres/schema/001_create_tables.sql"

def get_sql(sql_path: str) -> Optional[str]:
    """
    Loads SQL scripts from the given path

    :param sql_path: Path to the sql file
    :type sql_path: str
    :return: str | None
    """

    try:
        logger.info(f"Loading SQL file from {SQL_PATH}")
        with open(SQL_PATH, 'r', encoding='utf-8') as f:
            sql = f.read()
            if sql is not None:
                logger.info(f"SQL file successfully loaded from {SQL_PATH}")
                return sql
    except Exception as e:
        logger.error(f"Error loading SQL file from {SQL_PATH}: {e}")
        return None
    
def initialize_db(conn) -> None:
    """
    Executes SQL files using connection object to initialize the database

    :param conn: Connection object
    :type conn: Connection
    :return: None 
    """

    try:
        with conn.cursor() as curs:
            sql = get_sql(SQL_PATH)
            curs.execute(sql)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    initialize_db()