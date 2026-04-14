import logging
import threading
from typing import Any, Dict

from tg_ingestion_pipeline.loading.db.connect_db import get_connection
from tg_ingestion_pipeline.loading.db.insert_db import insert_message
from tg_ingestion_pipeline.loading.vectordb.weaviate_client import WeaviateClient
from tg_ingestion_pipeline.transformation.embeddings.embedding_model import Vectorizer
from tg_ingestion_pipeline.transformation.processing.data_loader import load_data_from_kafka

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TelegramDataPipeline:
    """Pipeline for consuming Telegram messages, persisting relational rows, and storing vectors in Weaviate."""

    def __init__(self, topic: str = 'extracted-data', group_id: str = 'processing-group'):
        self.topic = topic
        self.group_id = group_id
        self.vectorizer = Vectorizer()
        self.weaviate_client = WeaviateClient()

    def _normalize_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'message_id': int(message.get('message_id', 0)) if message.get('message_id') is not None else 0,
            'message_type': message.get('type') or message.get('message_type'),
            'message_timestamp': message.get('date') or message.get('message_timestamp'),
            'chat_id': int(message.get('chat_id', 0)) if message.get('chat_id') is not None else 0,
            'content': str(message.get('content', '')),
            'user_id': int(message.get('user_id')) if message.get('user_id') is not None else None,
            'username': message.get('username') or message.get('user_name'),
            'reply_to': int(message.get('reply_to')) if message.get('reply_to') is not None else None,
            'file_id': message.get('file_id'),
            'mime_type': message.get('mime_type'),
            'file_name': message.get('file_name'),
            'duration_seconds': int(message.get('duration')) if message.get('duration') is not None else message.get('duration_seconds'),
        }

    def _consume_message(self, message: Dict[str, Any]) -> None:
        normalized = self._normalize_message(message)

        if normalized['message_id'] == 0 or normalized['chat_id'] == 0:
            logger.warning('Skipping message with missing identifiers: %s', message)
            return

        conn = get_connection()
        if conn is None:
            logger.error('Database connection failed. Skipping relational insert for message %s', normalized['message_id'])
        else:
            try:
                insert_message(conn, normalized)
            except Exception as e:
                logger.error('Failed to insert message into relational database: %s', e)

        vector = self.vectorizer.vectorize(normalized)
        if not self.weaviate_client.upsert_message(normalized, vector=vector):
            logger.warning('Failed to store message %s in Weaviate.', normalized['message_id'])

    def start(self) -> None:
        logger.info('Starting pipeline consumer for topic %s and group %s', self.topic, self.group_id)
        try:
            for message in load_data_from_kafka(self.topic, self.group_id):
                self._consume_message(message)
        except Exception as e:
            logger.error('Pipeline stopped unexpectedly: %s', e)

    def start_async(self) -> threading.Thread:
        thread = threading.Thread(target=self.start, daemon=True, name='TelegramDataPipeline')
        thread.start()
        return thread
