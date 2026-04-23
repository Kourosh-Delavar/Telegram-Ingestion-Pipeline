from typing import Any, Dict, Generator, Optional
from confluent_kafka import Consumer, Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
import json
import logging
import threading
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv('.env.kafka')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use environment variables for Docker/local configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_SCHEMA_REGISTRY_URL = os.getenv('KAFKA_SCHEMA_REGISTRY_URL', 'http://schema-registry:8081')

DEFAULT_KAFKA_CONFIG = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
}

class KafkaOrchestrator:
    """
    KafkaOrchestrator is a class responsible for managing the Kafka producer and consuming messages from Kafka topics.
    It provides methods for producing JSON messages and reading them reliably from Kafka.
    """

    def __init__(self, conf: Optional[Dict[str, Any]] = None):
        conf = conf or DEFAULT_KAFKA_CONFIG
        self.producer = Producer(conf)
        self._stop_event = threading.Event()

    def stop(self) -> None:
        """Stop the consumer polling loop."""
        self._stop_event.set()

    @staticmethod
    def _delivery_report(err, msg) -> None:
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

    def send_message(self, topic: str, key: str, data: Dict[str, Any], schema_path: Optional[str] = None) -> None:
        try:
            if not self.producer:
                logger.error("Producer is not initialized.")
                return

            if schema_path:
                try:
                    with open(schema_path, 'r') as f:
                        schema_str = f.read()
                    sr_client = SchemaRegistryClient({'url': KAFKA_SCHEMA_REGISTRY_URL})
                    AvroSerializer(sr_client, schema_str)
                except Exception as e:
                    logger.warning(f"Failed to load Avro schema; sending raw JSON instead: {e}")

            self.producer.poll(0)
            self.producer.produce(
                topic=topic,
                key=str(key),
                value=json.dumps(data).encode('utf-8'),
                callback=self._delivery_report,
            )
            self.producer.flush()
            logger.info(f"Message sent to topic {topic} with key {key}")
        except Exception as e:
            logger.error(f"Failed to send message to kafka topic {topic}: {e}")

    def consume_message(self, topic: str, group_id: str) -> Generator[Dict[str, Any], None, None]:
        conf = {
            **DEFAULT_KAFKA_CONFIG,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
        }

        consumer = Consumer(conf)
        consumer.subscribe([topic])
        logger.info(f"Subscribed to topic {topic} with group ID {group_id}")

        try:
            while not self._stop_event.is_set():
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error(f"Consumer error: {msg.error()}")
                    continue

                try:
                    payload = msg.value().decode('utf-8')
                    yield json.loads(payload)
                except Exception as e:
                    logger.error(f"Failed to parse Kafka message payload: {e}")
        except Exception as e:
            logger.error(f"Failed to consume messages from kafka topic {topic}: {e}")
        finally:
            consumer.close()