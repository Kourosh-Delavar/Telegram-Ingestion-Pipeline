"""
Kafka Broker Test
This module contains unit tests for the kafka engine to ensure KafkaOrchestrator is functioning correctly.
"""

from typing import Dict, Any
from random import randint
import logging
import json
from kafka.kafka_engine import KafkaOrchestrator

# Configure logging for testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Helper function to generate test data 
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

# Test function for KafkaOrchestrator
def test_kafka_orchestrator() -> None:
    test_data = _generate_test_data()

    # Load Kafka configuration
    with open('src/kafka/configs/clients.json', 'r') as f:
        kafka_configs = json.load(f)
    conf = kafka_configs.get('message_handler', {})
    orchestrator = KafkaOrchestrator(conf)

    # Test: Sending a message to kafka topic 
    try:
        orchestrator.send_message(
            topic = "test_topic",
            key = test_data["file_id"],
            value = test_data
        )
        logging.info("KafkaOrchestrator test passed: Message sent successfully ")
    except Exception as e:
        logging.error(f"KafkaOrchestrator test failed: {e}")
    
    # Test: Consuming the message from kafka topic
    try:
        consumed_message = orchestrator.consume_message(
            topic = "test_topic",
            key = test_data["file_id"]
        )
        logging.info("KafkaOrchestrator test passed: Message consumed successfully")
        assert consumed_message == test_data, "Consumed message does not match the sent message"
        logging.info("KafkaOrchestrator test passed: Consumed message matches the sent message")
    except Exception as e:
        logging.error(f"KafkaOrchestrator test failed: {e}")

if __name__ == "__main__":
    test_kafka_orchestrator()