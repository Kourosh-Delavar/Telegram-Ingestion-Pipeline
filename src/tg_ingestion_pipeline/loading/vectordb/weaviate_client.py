import logging
import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

import weaviate


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

WEAVIATE_CLASS = "TelegramMessage"


def _build_auth_client(api_key: Optional[str]) -> Optional[Any]:
    if api_key:
        return weaviate.auth.Auth.api_key(api_key=api_key)
    return None


class WeaviateClient:
    """Client wrapper for Weaviate vector database operations."""

    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        load_dotenv('.env.weaviate')
        self.url = url or os.getenv('WEAVIATE_URL', 'http://localhost:8080')
        self.api_key = api_key or os.getenv('WEAVIATE_API_KEY')
        auth_client = _build_auth_client(self.api_key)
        self.client = weaviate.Client(url=self.url, auth_client_secret=auth_client)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        if self.client.schema.contains(WEAVIATE_CLASS):
            logger.info('Weaviate schema already exists.')
            return

        class_schema = {
            'class': WEAVIATE_CLASS,
            'vectorizer': 'none',  
            'vectorIndexConfig': {
                'distance': 'cosine', 
            },
            'properties': [
                {'name': 'message_id', 'dataType': ['int']},
                {'name': 'chat_id', 'dataType': ['int']},
                {'name': 'message_type', 'dataType': ['string']},
                {'name': 'content', 'dataType': ['text']},
                {'name': 'user_id', 'dataType': ['int']},
                {'name': 'username', 'dataType': ['string']},
                {'name': 'reply_to', 'dataType': ['int']},
                {'name': 'file_id', 'dataType': ['string']},
                {'name': 'mime_type', 'dataType': ['string']},
                {'name': 'file_name', 'dataType': ['string']},
                {'name': 'duration_seconds', 'dataType': ['int']},
            ],
        }

        self.client.schema.create_class(class_schema)
        logger.info('Created Weaviate class schema for TelegramMessage with custom vector support.')

    def upsert_message(self, message: Dict[str, Any], vector: Optional[List[float]] = None) -> bool:
        object_payload = {
            'message_id': int(message.get('message_id', 0)) if message.get('message_id') is not None else None,
            'chat_id': int(message.get('chat_id', 0)) if message.get('chat_id') is not None else None,
            'message_type': message.get('message_type'),
            'content': message.get('content'),
            'user_id': int(message.get('user_id')) if message.get('user_id') is not None else None,
            'username': message.get('username'),
            'reply_to': int(message.get('reply_to')) if message.get('reply_to') is not None else None,
            'file_id': message.get('file_id'),
            'mime_type': message.get('mime_type'),
            'file_name': message.get('file_name'),
            'duration_seconds': int(message.get('duration_seconds')) if message.get('duration_seconds') is not None else None,
        }

        try:
            self.client.data_object.create(
                data_object=object_payload,
                class_name=WEAVIATE_CLASS,
                vector=vector,
            )
            logger.info('Stored message in Weaviate vector database.')
            return True
        except Exception as e:
            logger.error(f'Error writing object to Weaviate: {e}')
            return False
