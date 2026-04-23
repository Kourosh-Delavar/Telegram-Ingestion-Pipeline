import logging
from typing import Dict, Any, Generator, Optional
from kafka.kafka_engine import KafkaOrchestrator

logger = logging.getLogger(__name__)


def load_data_from_kafka(
    topic: str,
    group_id: str,
    conf: Optional[Dict[str, Any]] = None,
    dead_letter_topic: Optional[str] = None,
) -> Generator[Dict[str, Any], None, None]:
    """
    Consume messages from a Kafka topic and yield each parsed message.

    :param topic: the Kafka topic from which messages should be consumed
    :param group_id: the consumer group ID
    :param conf: optional Kafka client configuration overrides
    :return: Generator of parsed message dictionaries
    """

    try:
        orchestrator = KafkaOrchestrator(conf)
        for message in orchestrator.consume_message(topic, group_id, dead_letter_topic=dead_letter_topic):
            if message is not None:
                logger.info(f"Message consumed from topic {topic}")
                yield message
            else:
                logger.warning(f"Received empty message from topic {topic}")
    except Exception as e:
        logger.error(f"Failed to load data from kafka topic {topic}: {e}")
        return
