from typing import Dict, Any, Generator 
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka import Consumer
import json
import logging


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KafkaOrchestrator:
    """
    KafkaOrchestrator is a class responsible for managing the Kafka producer and sending messages to specified Kafka topics.
    It provides methods for initializing the producer, reporting delivery results, and sending messages in JSON format to Kafka topics.
    
    :param conf: A dictionary containing the configuration parameters for the Kafka producer, such as bootstrap servers, client ID, acknowledgment settings, and compression type.
    :type conf: Dict[str, Any]
    """

    def __init__(self, conf: Dict[str, Any]):
        self.producer = Producer(conf or {})


    @staticmethod
    def _delivery_report(err, msg) -> None:
        """
        Report the delivery result of a message sent to a topic by the producer.
        
        :param err: error information if the message failed to deliver, otherwise None
        :param msg: the message that was produced
        :return: None
        """

        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")


    def send_message(self, topic: str, key: str, data: Dict[str, Any], schema_path: str) -> None:
        """
        Send a message to a specified Kafka topic with the given key and data.
        
        :param self: KafkaOrchestrator instance
        :param topic: the kafka topic to which the message should be sent
        :type topic: str
        :param key: the key to be used for routing the message to the appropriate partition
        :type key: str
        :param data: the message content to be sent, which will be serialized to JSON format
        :type data: Dict[str, Any]
        :param schema_path: the file path to the Avro schema that will be used for serializing the message
        :type schema_path: str 
        :return: None
        """

        try:
            if not self.producer:
                logger.error("Producer is not initialized.")
                return
            
            # Serialize the data to Avro format using the schema from schema registry
            try:
                with open(schema_path, 'r') as f:
                    schema_str = f.read()
            except Exception as e:
                logger.error(f"Failed to read schema file: {e}")
                schema_str = None    
            sr_client = SchemaRegistryClient({'url': 'http://localhost:8081'})
            avro_serializer = AvroSerializer(sr_client, schema_str)

            # Produce the message to the specified topic
            self.producer.poll(0)
            self.producer.produce(
                topic = topic,
                key = key,
                value = json.dumps(data).encode('utf-8'),
                callback = self._delivery_report 
            )
            self.producer.flush()
            logger.info(f"Message sent to topic {topic} with key {key}")
        except Exception as e:
            logger.error(f"Failed to send message to kafka topic {topic}: {e}")


    def consume_message(self, topic: str, group_id: str) -> Generator[str, None, None]:
        """"
        Consume messages from a specified Kafka topic using a consumer group ID.
        
        :param self: KafkaOrchestrator instance
        :param topic: the kafka topic from which messages should be consumed
        :type topic: str
        :param group_id: the consumer group ID to be used for consuming messages
        :type group_id: str
        :return: Generator[str, None, None]
        """

        # Configure the consumer
        # TODO: make the conf configurable and load it from a config file
        conf = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        }
        
        consumer = Consumer(conf)
        consumer.subscribe([topic])
        logger.info(f"Subscribed to topic {topic} with group ID {group_id}")

        # Poll for messages
        try:
            while not self._stop_event.is_set():
                msg = consumer.poll(1.0) # TODO: make the timeout configurable
                if msg is None:
                    continue
                if msg.error():
                    logger.error(f"Consumer error: {msg.error()}")
                    continue
                yield json.loads(msg.value().decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to consume messages from kafka topic {topic}: {e}")
        finally:
            consumer.close()