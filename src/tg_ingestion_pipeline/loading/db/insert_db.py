import logging
from typing import Optional
# from psycopg2.extras import execute_batch
from .connect_db import get_connection
from .utils.get_sql_file import get_sql

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

INSERT_SQL_PATH = "./db/postgres/utils/001_insert_data.sql"

def insert_data(conn) -> bool:
    """
    Insert message data into the database using connection object

    :param conn: Connection object
    :type conn: Connection
    :return: bool
    """

    try:
        with get_sql(INSERT_SQL_PATH) as query:
            logger.info("Inserting data to the database...") # TODO: Mention DB_NAME in the logging message
            with conn.cursor() as curs:
                curs.execute(query)
                affected = curs.rowcount
                curs.commit()
                logger.info("Insert executed. verifying...")

                if affected == 0:
                    logger.error(f"Query Executed but affected 0 rows | query: {query}")
                    return False
                else:
                    logger.info(f"Query executed and affected {affected} row(s) successfully")
                    return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting data: {e}")
        return False
    finally:
        curs.close()
        conn.close()

# TODO: Add execute_batch capability 