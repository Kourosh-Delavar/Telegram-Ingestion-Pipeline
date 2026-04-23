import logging
import threading
from typing import Any, Dict, List, Optional

from kafka.kafka_engine import KafkaOrchestrator
from tg_ingestion_pipeline.app.message_processing import MessageProcessingService
from tg_ingestion_pipeline.loading.db.insert_db import insert_message
from tg_ingestion_pipeline.loading.vectordb.weaviate_client import WeaviateClient
from tg_ingestion_pipeline.core.settings import get_settings
from tg_ingestion_pipeline.loading.db.connect_db import db_connection
from tg_ingestion_pipeline.transformation.processing.data_loader import load_data_from_kafka

logger = logging.getLogger(__name__)


class TelegramDataPipeline:
    """Pipeline for consuming Telegram messages, persisting relational rows, and storing vectors in Weaviate."""

    def __init__(self, topic: Optional[str] = None, group_id: Optional[str] = None):
        settings = get_settings()
        self.topic = topic or settings.kafka_topic_extracted
        self.group_id = group_id or settings.kafka_group_processing
        self.dead_letter_topic = settings.kafka_topic_dlq
        self.kafka = KafkaOrchestrator()
        self.weaviate_client = WeaviateClient()
        self.processor = MessageProcessingService(
            repository=_PostgresMessageRepository(),
            vector_store=_WeaviateVectorStore(self.weaviate_client),
            dlq_publisher=_DlqPublisher(self.kafka, self.dead_letter_topic),
        )

    def _consume_message(self, message: Dict[str, Any]) -> None:
        success = self.processor.process(message)
        if not success:
            logger.warning("Message processing failed and was sent to DLQ.")

    def start(self) -> None:
        logger.info('Starting pipeline consumer for topic %s and group %s', self.topic, self.group_id)
        try:
            for message in load_data_from_kafka(self.topic, self.group_id, dead_letter_topic=self.dead_letter_topic):
                try:
                    self._consume_message(message)
                except Exception as e:
                    logger.error("Unexpected message processing error: %s", e)
                    self.kafka.send_message(
                        topic=self.dead_letter_topic,
                        key="pipeline-exception",
                        data={"error": str(e), "payload": message},
                    )
        except Exception as e:
            logger.error('Pipeline stopped unexpectedly: %s', e)

    def start_async(self) -> threading.Thread:
        thread = threading.Thread(target=self.start, daemon=True, name='TelegramDataPipeline')
        thread.start()
        return thread


class _PostgresMessageRepository:
    def upsert(self, message: Dict[str, Any]) -> bool:
        with db_connection() as conn:
            if conn is None:
                logger.error("No database connection available for message=%s", message.get("message_id"))
                return False
            return insert_message(conn, message)


class _WeaviateVectorStore:
    def __init__(self, client: WeaviateClient) -> None:
        self.client = client

    def upsert(self, message: Dict[str, Any], vector: Optional[List[float]]) -> bool:
        return self.client.upsert_message(message, vector=vector)


class _DlqPublisher:
    def __init__(self, kafka: KafkaOrchestrator, topic: str) -> None:
        self.kafka = kafka
        self.topic = topic

    def publish(self, key: str, payload: Dict[str, Any]) -> None:
        self.kafka.send_message(topic=self.topic, key=key, data=payload)
