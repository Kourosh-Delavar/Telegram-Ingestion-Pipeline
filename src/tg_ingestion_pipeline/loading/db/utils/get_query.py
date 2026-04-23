import logging
from typing import Optional

logger = logging.getLogger(__name__)

def get_query(sql_path: str) -> Optional[str]:
    """
    Loads query from a given path

    :param sql_path: Path to the sql file
    :type sql_path: str
    :return: str | None
    """

    try:
        logger.info(f"Loading SQL file from {sql_path} ...")
        with open(sql_path, 'r', encoding='utf-8') as f:
            query = f.read()
            if query is not None:
                logger.info(f"Query successfully loaded from {sql_path}")
                return query
    except Exception as e:
        logger.error(f"Error loading query from {sql_path}: {e}")
        return None