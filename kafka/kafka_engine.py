from typing import Dict, Any
from confluent_kafka import Producer
import json
import logging



class KafkaOrchestrator:
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
            self.producer.produce(
                topic = topic,
                key = key,
                value = json.dumps(data or {}),
                callback = self._delivery_report 
            )
            self.producer.flush(timeout=10.0)
        except Exception as e:
            logging.error(f"Failed to send message to kafka topic {topic}: {e}")
