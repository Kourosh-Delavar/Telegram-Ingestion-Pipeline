import logging
from functools import lru_cache
from pathlib import Path
from .utils.get_query import get_query

logger = logging.getLogger(__name__)

def _get_sql_path() -> Path:
    """
    Resolve the SQL schema file path, handling both direct execution and installed package scenarios.
    
    :return: Path to the SQL file
    :rtype: Path
    """
    # Try to find the db directory by looking for it relative to this file
    current_file = Path(__file__).resolve()
    
    # Walk up the directory tree looking for the db directory
    search_dir = current_file.parent
    for _ in range(10):  # Search up to 10 levels up
        search_dir = search_dir.parent
        db_path = search_dir / "db" / "postgres" / "schema" / "001_create_tables.sql"
        if db_path.exists():
            return db_path
    
    # Fallback: try common relative paths
    fallbacks = [
        Path(__file__).resolve().parents[3] / "db" / "postgres" / "schema" / "001_create_tables.sql",
        Path.cwd() / "db" / "postgres" / "schema" / "001_create_tables.sql",
    ]
    
    for fallback_path in fallbacks:
        if fallback_path.exists():
            return fallback_path
    
    # If still not found, return the most likely path and let get_query handle the error
    return Path(__file__).resolve().parents[3] / "db" / "postgres" / "schema" / "001_create_tables.sql"

INIT_SQL_PATH = _get_sql_path()

def initialize_db(conn) -> bool:
    """
    Executes schema creation queries using the provided connection object.

    :param conn: Connection object
    :return: bool
    """

    try:
        logger.info("Initializing the relational database schema...")
        with conn.cursor() as curs:
            query = _init_query()
            curs.execute(query)
        conn.commit()
        logger.info("Database schema initialized successfully")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initializing database: {e}")
        return False


@lru_cache(maxsize=1)
def _init_query() -> str:
    query = get_query(str(INIT_SQL_PATH))
    if not query:
        raise RuntimeError(f"Failed to load SQL schema from {INIT_SQL_PATH}")
    return query
