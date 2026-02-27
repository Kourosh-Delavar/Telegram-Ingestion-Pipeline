from typing import Dict, Any
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
    def _delivery_report(self, err, msg) -> None:
        """
        Report the devlivery result of a message sent to a topic by the producer.
        
        :param self: KafkaOrchestrator instance 
        :param err: error information if the message failed to deliver, otherwise None
        :param msg: the message that was produced
        :return: None
        """


        if err is not None:
            logging.error(f"Message delivery failed: {err}")
        else:
            logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")


    def send_message(self, topic: str, key: str, data: Dict[str, Any]) -> None:
        """
        Send a message to a specified Kafka topic with the given key and data.
        
        :param self: KafkaOrchestrator instance
        :param topic: the kafka topic to which the message should be sent
        :type topic: str
        :param key: the key to be used for routing the message to the appropriate partition
        :type key: str
        :param data: the message content to be sent, which will be serialized to JSON format
        :type data: Dict[str, Any]
        :return: None
        """

        try:
            if not self.producer:
                logging.error("Producer is not initialized.")
                return
            
            # Serialize the data to Avro format using the schema from the schema registry
            try:
                with open('kafka/schemas/schema.json', 'r') as f:
                    schema_str = f.read()
            except Exception as e:
                logging.error(f"Failed to read schema file: {e}")
                return
            sr_client = SchemaRegistryClient({'url': 'http://localhost:8081'})
            avro_serializer = AvroSerializer(sr_client, schema_str)

            # Produce the message to the specified topic
            self.producer.produce(
                topic = topic,
                key = key,
                value = avro_serializer(data, SerializationContext(topic, MessageField.VALUE)),
                callback = self._delivery_report 
            )
            self.producer.flush()
            logging.info(f"Message sent to topic {topic} with key {key}")
        except Exception as e:
            logging.error(f"Failed to send message to kafka topic {topic}: {e}")


    def consume_messages(self, topic: str, group_id: str) -> None:
        """"
        Consume messages from a specified Kafka topic using a consumer group ID.
        
        :param self: KafkaOrchestrator instance
        :param topic: the kafka topic from which messages should be consumed
        :type topic: str
        :param group_id: the consumer group ID to be used for consuming messages
        :type group_id: str
        :return: None
        """

        pass
