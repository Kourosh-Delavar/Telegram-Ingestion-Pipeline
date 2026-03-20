import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_sql(sql_path: str) -> Optional[str]:
    """
    Loads SQL scripts from the given path

    :param sql_path: Path to the sql file
    :type sql_path: str
    :return: str | None
    """

    try:
        logger.info(f"Loading SQL file from {sql_path}")
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql = f.read()
            if sql is not None:
                logger.info(f"SQL file successfully loaded from {sql_path}")
                return sql
    except Exception as e:
        logger.error(f"Error loading SQL file from {sql_path}: {e}")
        return None