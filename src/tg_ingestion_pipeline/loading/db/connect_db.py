import logging
from contextlib import contextmanager
from typing import Generator, Optional

from psycopg2.pool import SimpleConnectionPool

from tg_ingestion_pipeline.core.settings import get_settings


logger = logging.getLogger(__name__)

_POOL: Optional[SimpleConnectionPool] = None


def init_connection_pool(minconn: int = 1, maxconn: int = 10) -> bool:
    global _POOL
    if _POOL is not None:
        return True

    settings = get_settings()
    try:
        _POOL = SimpleConnectionPool(minconn=minconn, maxconn=maxconn, **settings.db_config)
        logger.info("PostgreSQL connection pool initialized")
        return True
    except Exception as exc:
        logger.error("Error initializing database connection pool: %s", exc)
        _POOL = None
        return False


def get_connection():
    if _POOL is None and not init_connection_pool():
        return None
    assert _POOL is not None
    try:
        return _POOL.getconn()
    except Exception as exc:
        logger.error("Error acquiring connection from pool: %s", exc)
        return None


def release_connection(conn) -> None:
    if _POOL is None or conn is None:
        return
    _POOL.putconn(conn)


def close_connection_pool() -> None:
    global _POOL
    if _POOL is None:
        return
    _POOL.closeall()
    _POOL = None


@contextmanager
def db_connection() -> Generator:
    conn = get_connection()
    try:
        yield conn
    finally:
        if conn is not None:
            release_connection(conn)