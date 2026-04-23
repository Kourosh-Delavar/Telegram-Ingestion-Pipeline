import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[3]

# Load environment once at process startup.
load_dotenv(ROOT_DIR / ".env.token")
load_dotenv(ROOT_DIR / ".env.postgres")
load_dotenv(ROOT_DIR / ".env.weaviate")
load_dotenv(ROOT_DIR / ".env.kafka")


@dataclass(frozen=True)
class Settings:
    bot_token: str
    kafka_bootstrap_servers: str
    kafka_schema_registry_url: str
    kafka_topic_extracted: str
    kafka_topic_dlq: str
    kafka_group_processing: str
    weaviate_url: str
    weaviate_api_key: str
    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str

    @property
    def db_config(self) -> Dict[str, Any]:
        return {
            "host": self.postgres_host,
            "port": self.postgres_port,
            "user": self.postgres_user,
            "password": self.postgres_password,
            "database": self.postgres_db,
        }


def get_settings() -> Settings:
    return Settings(
        bot_token=os.getenv("BOT_TOKEN", ""),
        kafka_bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        kafka_schema_registry_url=os.getenv("KAFKA_SCHEMA_REGISTRY_URL", "http://schema-registry:8081"),
        kafka_topic_extracted=os.getenv("KAFKA_TOPIC_EXTRACTED", "extracted-data"),
        kafka_topic_dlq=os.getenv("KAFKA_TOPIC_DLQ", "extracted-data-dlq"),
        kafka_group_processing=os.getenv("KAFKA_GROUP_PROCESSING", "processing-group"),
        weaviate_url=os.getenv("WEAVIATE_URL", "http://weaviate:8080"),
        weaviate_api_key=os.getenv("WEAVIATE_API_KEY", ""),
        postgres_host=os.getenv("POSTGRES_HOST", "postgres"),
        postgres_port=int(os.getenv("POSTGRES_PORT", 5432)),
        postgres_user=os.getenv("POSTGRES_USER", "test_user"),
        postgres_password=os.getenv("POSTGRES_PASSWORD", "123456789"),
        postgres_db=os.getenv("POSTGRES_DB", "test_db"),
    )
