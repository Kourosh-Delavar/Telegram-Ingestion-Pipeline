import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import weaviate
from weaviate.collections.classes.config import Configure, Property, DataType, VectorDistances
from tg_ingestion_pipeline.core.settings import get_settings


logger = logging.getLogger(__name__)

WEAVIATE_CLASS = "TelegramMessage"


def _build_auth_client(api_key: Optional[str]) -> Optional[Any]:
    """Build authentication credentials for Weaviate v4."""
    if api_key and api_key.strip():
        logger.info("Using API key authentication for Weaviate")
        return weaviate.auth.ApiKey(api_key=api_key)
    return None


def _parse_weaviate_url(url: str) -> tuple:
    """
    Parse Weaviate URL and extract host and port.
    
    :param url: URL string (e.g., http://weaviate:8080 or https://cluster.weaviate.network)
    :return: Tuple of (host, port)
    """
    parsed = urlparse(url)
    
    host = parsed.hostname or 'localhost'
    port = parsed.port or (443 if parsed.scheme == 'https' else 8080)
    
    logger.debug(f"Parsed Weaviate URL: host={host}, port={port}")
    return host, port


class WeaviateClient:
    """Client wrapper for Weaviate vector database operations (v4 API)."""

    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        settings = get_settings()
        self.url = url or settings.weaviate_url
        self.api_key = api_key or settings.weaviate_api_key
        self.client = None
        self.connected = False
        
        logger.info(f"Initializing Weaviate client for {self.url}")
        
        # Try to connect, but don't fail if Weaviate is not available
        try:
            self._connect()
        except Exception as e:
            logger.warning(f"Weaviate connection failed (will retry on first use): {e}")
    
    def _connect(self) -> None:
        """Connect to Weaviate server."""
        
        if self.client is not None:
            return  # Already connected
        
        # Parse URL and initialize client
        http_host, http_port = _parse_weaviate_url(self.url)
        auth_credentials = _build_auth_client(self.api_key)
        
        # Use connect_to_local for docker deployment
        # skip_init_checks=True to skip gRPC health checks when gRPC port is not exposed
        self.client = weaviate.connect_to_local(
            host=http_host,
            port=http_port,
            auth_credentials=auth_credentials,
            skip_init_checks=True  # Skip gRPC checks if not available
        )
        
        logger.info(f"Successfully connected to Weaviate at {self.url}")
        
        # Manual readiness check using HTTP only
        try:
            ready = self.client.is_ready()
            if not ready:
                logger.warning("Weaviate server readiness check failed, but continuing anyway")
            else:
                logger.info("Weaviate server is ready")
                self.connected = True
        except Exception as e:
            logger.warning(f"Failed to verify Weaviate readiness: {e}")
        
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Ensure TelegramMessage schema exists in Weaviate. Non-blocking if client unavailable."""
        if self.client is None:
            logger.debug("Weaviate client not available, skipping schema creation")
            return
        
        try:
            # Check if collection exists
            if self.client.collections.exists(WEAVIATE_CLASS):
                logger.info(f'Weaviate collection "{WEAVIATE_CLASS}" already exists.')
                return

            logger.info(f'Creating Weaviate collection "{WEAVIATE_CLASS}"...')
            
            # Create collection in v4 API using correct imports
            self.client.collections.create(
                name=WEAVIATE_CLASS,
                vectorizer_config=Configure.Vectorizer.none(),
                vector_index_config=Configure.VectorIndex.hnsw(distance_metric=VectorDistances.COSINE),
                properties=[
                    Property(name="message_id", data_type=DataType.INT),
                    Property(name="chat_id", data_type=DataType.INT),
                    Property(name="message_type", data_type=DataType.TEXT),
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="user_id", data_type=DataType.INT),
                    Property(name="username", data_type=DataType.TEXT),
                    Property(name="reply_to", data_type=DataType.INT),
                    Property(name="file_id", data_type=DataType.TEXT),
                    Property(name="mime_type", data_type=DataType.TEXT),
                    Property(name="file_name", data_type=DataType.TEXT),
                    Property(name="duration_seconds", data_type=DataType.INT),
                ]
            )
            logger.info(f'Successfully created Weaviate collection "{WEAVIATE_CLASS}".')
            
        except Exception as e:
            logger.warning(f"Error ensuring Weaviate schema: {e}")

    def upsert_message(self, message: Dict[str, Any], vector: Optional[List[float]] = None) -> bool:
        """Upsert a message with optional vector embedding to Weaviate."""
        # Try to connect if not already connected
        if self.client is None:
            try:
                self._connect()
            except Exception as e:
                logger.warning(f'Could not connect to Weaviate for upsert: {e}')
                return False
        
        if self.client is None:
            logger.warning('Weaviate client unavailable, skipping message upsert')
            return False
        
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
            collection = self.client.collections.get(WEAVIATE_CLASS)
            collection.data.insert(
                properties=object_payload,
                vector=vector,
            )
            logger.info(f'Successfully stored message {object_payload.get("message_id")} in Weaviate.')
            return True
        except Exception as e:
            logger.error(f'Error writing object to Weaviate: {e}')
            return False
