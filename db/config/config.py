from dotenv import load_dotenv 
import os 
 
load_dotenv('.env.postgres')
 
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),  # Default to 'postgres' for Docker
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
    "user": os.getenv("POSTGRES_USER", "test_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "123456789"),
    "database": os.getenv("POSTGRES_DB", "test_db")
}
 
TABLE_NAME = "messages"
