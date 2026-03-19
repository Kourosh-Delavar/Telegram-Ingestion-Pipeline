from dotenv import load_dotenv 
import os 
 
load_dotenv('.env.postgres')
 
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB")
}
 
TABLE_NAME = "messages"