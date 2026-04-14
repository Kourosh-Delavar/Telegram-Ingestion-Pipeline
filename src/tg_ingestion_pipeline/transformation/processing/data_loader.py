import logging
from typing import Dict, Any, Generator, Optional
from kafka.kafka_engine import KafkaOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_data_from_kafka(
    topic: str,
    group_id: str,
    conf: Optional[Dict[str, Any]] = None,
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
        for message in orchestrator.consume_message(topic, group_id):
            if message is not None:
                logger.info(f"Message consumed from topic {topic}")
                yield message
            else:
                logger.warning(f"Received empty message from topic {topic}")
    except Exception as e:
        logger.error(f"Failed to load data from kafka topic {topic}: {e}")
        return
