import logging
# from psycopg2.extras import execute_batch
# from pathlib import Path
    # TODO: Use pathlib for better paths
from .utils.get_query import get_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Path to SQL file used for initializing the database 
INIT_SQL_PATH = "./db/postgres/schema/001_create_tables.sql"

def initialize_db(conn) -> bool:
    """
    Executes query using connection object to initialize the database

    :param conn: Connection object
    :type conn: Connection
    :return: bool
    """

    try:
        with conn.cursor() as curs:
            query = get_query(INIT_SQL_PATH)
            curs.execute(query)
            curs.commit()
            logger.info("Database initialized successfully")
            return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initializing database: {e}")
        return False
    finally:
        curs.close()
        conn.close()

if __name__ == "__main__":
    initialize_db()

# TODO: Add batch execution capability using execute_batch