import logging
from pathlib import Path
from .utils.get_query import get_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[3]
INIT_SQL_PATH = BASE_DIR / "db" / "postgres" / "schema" / "001_create_tables.sql"

def initialize_db(conn) -> bool:
    """
    Executes schema creation queries using the provided connection object.

    :param conn: Connection object
    :return: bool
    """

    try:
        logger.info("Initializing the relational database schema...")
        with conn.cursor() as curs:
            query = get_query(str(INIT_SQL_PATH))
            curs.execute(query)
        conn.commit()
        logger.info("Database schema initialized successfully")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initializing database: {e}")
        return False
    finally:
        conn.close()
