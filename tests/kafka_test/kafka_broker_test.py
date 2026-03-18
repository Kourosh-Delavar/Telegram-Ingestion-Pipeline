"""
Kafka Broker Test
This module contains unit tests for the kafka engine to ensure KafkaOrchestrator is functioning correctly.
"""

from typing import Dict, Any, Generator
from random import randint
import logging
import json
from pathlib import Path 
from kafka.kafka_engine import KafkaOrchestrator

# Configure logging for testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _generate_test_data() -> Dict[str, Any]:
    return {
        "file_id": "test_file_id",
        "type": "test_message_type",
        "content": "test_content",
        "file_name": "test_file_name",
        "message_id": randint(1000, 9999),
        "chat_id": randint(1000, 9999),
        "user_id": randint(1000, 9999),
        "username": "test_username",
        "reply_to": randint(1000, 9999),
        "duration": randint(1000, 9999),
        "date": "test_date",
        "mime_type": "test_mime_type",
    }

def test_kafka_orchestrator() -> None:
    test_data = _generate_test_data()

    # Load Kafka configuration
    client_config_path = Path(__file__).parent / "configs" / "client_test.json"
    try:
        logging.info(f"Loading kafka configuration from {client_config_path}")
        with open(client_config_path, 'r') as f:
            kafka_configs = json.load(f) or {}
        if kafka_configs is None:
            logging.error(f"Kafka configuration is empty in {client_config_path}")
            conf = {}
        else:
            logging.info(f"Kafka configuration loaded successfully from {client_config_path}")
            conf = kafka_configs.get("test_handler", {})
    except Exception as e:
        logging.error(f"Failed to load kafka configuration from {client_config_path}: {e}")
        conf = {}

    orchestrator = KafkaOrchestrator(conf)

    topic = f"test_topic_{test_data['message_id']}"
    # Test: Sending a message to kafka topic 
    try:
        schema_path = Path(__file__).parent / "schemas" / "schema.json"
        orchestrator.send_message(
            topic = topic,
            key = test_data["file_id"],
            data = test_data,
            schema_path = str(schema_path)
        )
        logging.info("KafkaOrchestrator test passed: Message sent successfully ")
    except Exception as e:
        logging.error(f"KafkaOrchestrator test failed: {e}")
    
    # Test: Consuming the message from kafka topic
    try:
        consumed_message: Generator[str, None, None] = orchestrator.consume_message(
            topic = topic,
            group_id = test_data["file_id"]
        )
        logging.info("KafkaOrchestrator test passed: Message consumed successfully")
        assert json.loads(next(consumed_message)) == test_data, "Consumed message does not match the sent message"
        logging.info("KafkaOrchestrator test passed: Consumed message matches the sent message")
    except Exception as e:
        logging.error(f"KafkaOrchestrator test failed: {e}")

if __name__ == "__main__":
    test_kafka_orchestrator()