import logging
from typing import Optional
# from psycopg2.extras import execute_batch
from pathlib import Path
from .connect_db import get_connection
from .utils.get_sql_file import get_sql

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Path to SQL file used for initializing the database 
INIT_SQL_PATH = "./db/postgres/schema/001_create_tables.sql"

def initialize_db(conn) -> None:
    """
    Executes SQL files using connection object to initialize the database

    :param conn: Connection object
    :type conn: Connection
    :return: None 
    """

    try:
        with conn.cursor() as curs:
            sql = get_sql(INIT_SQL_PATH)
            curs.execute(sql)
            curs.commit()
            logger.info("Database initialized successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        curs.close()
        conn.close()

if __name__ == "__main__":
    initialize_db()

# TODO: Add batch execution capability using execute_batch