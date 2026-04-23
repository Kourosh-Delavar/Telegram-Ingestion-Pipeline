import logging
from typing import Any, Dict, Optional

from tg_ingestion_pipeline.app.ports import DeadLetterPublisher, MessageRepository, VectorStore
from tg_ingestion_pipeline.transformation.embeddings.embedding_model import Vectorizer


logger = logging.getLogger(__name__)


class MessageProcessingService:
    def __init__(
        self,
        repository: MessageRepository,
        vector_store: VectorStore,
        vectorizer: Optional[Vectorizer] = None,
        dlq_publisher: Optional[DeadLetterPublisher] = None,
    ) -> None:
        self.repository = repository
        self.vector_store = vector_store
        self.vectorizer = vectorizer or Vectorizer()
        self.dlq_publisher = dlq_publisher

    def normalize(self, message: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "message_id": int(message.get("message_id", 0)) if message.get("message_id") is not None else 0,
            "message_type": message.get("type") or message.get("message_type"),
            "message_timestamp": message.get("date") or message.get("message_timestamp"),
            "chat_id": int(message.get("chat_id", 0)) if message.get("chat_id") is not None else 0,
            "content": str(message.get("content", "")),
            "user_id": int(message.get("user_id")) if message.get("user_id") is not None else None,
            "username": message.get("username") or message.get("user_name"),
            "reply_to": int(message.get("reply_to")) if message.get("reply_to") is not None else None,
            "file_id": message.get("file_id"),
            "mime_type": message.get("mime_type"),
            "file_name": message.get("file_name"),
            "duration_seconds": int(message.get("duration")) if message.get("duration") is not None else message.get("duration_seconds"),
        }

    def process(self, raw_message: Dict[str, Any]) -> bool:
        normalized = self.normalize(raw_message)
        if normalized["message_id"] == 0 or normalized["chat_id"] == 0:
            logger.warning("Skipping message with missing identifiers: %s", raw_message)
            self._publish_dlq("missing-identifiers", raw_message, "missing message_id/chat_id")
            return False

        if not self.repository.upsert(normalized):
            self._publish_dlq(str(normalized["message_id"]), raw_message, "failed relational write")
            return False

        vector = self.vectorizer.vectorize(normalized)
        if not self.vector_store.upsert(normalized, vector):
            self._publish_dlq(str(normalized["message_id"]), raw_message, "failed vector write")
            return False

        return True

    def _publish_dlq(self, key: str, payload: Dict[str, Any], reason: str) -> None:
        if self.dlq_publisher is None:
            return
        self.dlq_publisher.publish(
            key=key,
            payload={"reason": reason, "payload": payload},
        )
