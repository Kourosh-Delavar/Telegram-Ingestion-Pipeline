"""
Data loader module: Consume serialized messages from Kafka topic, deserialize them using the provided Avro schema and yield the deserialized messages for further processing in the pipeline.  
"""

import logging 
from typing import Dict, Any
import json
from kafka.kafka_engine import KafkaOrchestrator

# Configure logging 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def load_data_from_kafka(topic: str, group_id: str) -> Dict[str, Any]:
    """
    Consume message from kafka topic and yield the deserialized message

    :param topic: the kafka topic from which messages should be consumed
    :type topic: str
    :param group_id: the consumer group ID 
    :type group_id: str
    :return: Generator[Dict[str, Any], None, None]
    """

    try:
        orchestrator = KafkaOrchestrator()
        for message in orchestrator.consume_message(topic, group_id):
            if message is not None:
                logging.info(f"Message consumed from topic {topic} and ")
                # Deserialize the message 
                try:
                    deserialized_message: str = message.decode('utf-8')
                    logging.info(f"Message deserialized successfully")
                except Exception as e:
                    logging.error(f"Failed to deserialize message: {e}")
                # Parse to JSON
                try:
                    json_message: Dict[str, Any] = json.loads(deserialized_message)
                    logging.info(f"Message parsed to JSON successfully")
                    yield json_message
                except Exception as e:
                    logging.error(f"Failed to parse message to JSON: {e}")
            else:
                logging.warning(f"Received empty message from topic {topic}")
    except Exception as e:
        logging.error(f"Failed to load data from kafka topic {topic}: {e}")           