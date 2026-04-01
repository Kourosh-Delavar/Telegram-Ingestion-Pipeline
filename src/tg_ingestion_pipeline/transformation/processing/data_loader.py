import logging 
from typing import Dict, Any, AsyncGenerator
import json
from kafka.kafka_engine import KafkaOrchestrator

# Configure logging 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def load_data_from_kafka(topic: str, group_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Consume message from kafka topic and yield the message. 

    :param topic: the kafka topic from which messages should be consumed
    :type topic: str
    :param group_id: the consumer group ID 
    :type group_id: str
    :return: AsyncGenerator[Dict[str, Any], None] 
    """

    try:
        orchestrator = KafkaOrchestrator()
        for message in orchestrator.consume_message(topic, group_id):
            if message is not None:
                logging.info(f"Message consumed from topic {topic} and ")
                yield message
            else:
                logging.warning(f"Received empty message from topic {topic}")
    except Exception as e:
        logging.error(f"Failed to load data from kafka topic {topic}: {e}")           