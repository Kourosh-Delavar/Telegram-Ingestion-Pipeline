import logging
from typing import Any, Dict

from kafka.kafka_engine import KafkaOrchestrator
from tg_ingestion_pipeline.core.settings import get_settings


logger = logging.getLogger(__name__)

_KAFKA: KafkaOrchestrator | None = None


def _publisher() -> KafkaOrchestrator:
    global _KAFKA
    if _KAFKA is None:
        _KAFKA = KafkaOrchestrator()
    return _KAFKA


def publish_extracted_message(key: str, data: Dict[str, Any]) -> None:
    settings = get_settings()
    _publisher().send_message(topic=settings.kafka_topic_extracted, key=key, data=data)
    logger.info("Published extracted message to Kafka topic=%s key=%s", settings.kafka_topic_extracted, key)
