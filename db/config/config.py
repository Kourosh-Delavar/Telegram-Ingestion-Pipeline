from dotenv import load_dotenv 
import os 

# Load environment variables from .env file 
load_dotenv('.env.postgres')

# Database configuration 
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB")
}

# Name of the table to store messages 
TABLE_NAME = "messages"