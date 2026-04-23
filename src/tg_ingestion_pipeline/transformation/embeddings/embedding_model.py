from logging import getLogger
from typing import Any, Dict, List

logger = getLogger(__name__)

class Vectorizer:
    """
    Semantic vectorizer using sentence-transformers for RAG applications.
    Generates high-quality embeddings suitable for LLM retrieval-augmented generation.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vectorizer with a sentence-transformers model.

        :param model_name: Name of the sentence-transformers model to use
        :type model_name: str
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading sentence-transformers model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            embedding_dim = self._get_embedding_dimension()
            logger.info(f"Model loaded successfully. Embedding dimension: {embedding_dim}")
        except ImportError:
            logger.error("sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise

    def vectorize(self, data: Dict[str, Any]) -> List[float]:
        """
        Vectorize the input data using semantic embeddings for RAG applications.

        :param data: The input data to be vectorized
        :type data: Dict[str, Any]
        :return: A list of floats representing the semantic embedding
        """

        logger.debug(f"Vectorizing data: {data}")

        # Extract and combine text content
        content = str(data.get("content", "") or "").strip()
        metadata_parts = []

        # Add relevant metadata for context
        if data.get("message_type"):
            metadata_parts.append(f"Type: {data['message_type']}")
        if data.get("username"):
            metadata_parts.append(f"User: {data['username']}")
        if data.get("file_name"):
            metadata_parts.append(f"File: {data['file_name']}")
        if data.get("mime_type"):
            metadata_parts.append(f"MIME: {data['mime_type']}")

        metadata = " | ".join(metadata_parts)

        # Combine content and metadata
        if content and metadata:
            full_text = f"{content}\n\nMetadata: {metadata}"
        elif content:
            full_text = content
        elif metadata:
            full_text = f"Metadata: {metadata}"
        else:
            logger.warning("Empty payload received for embedding; returning zero vector.")
            dimension = self._get_embedding_dimension()
            return [0.0] * dimension

        try:
            # Generate semantic embedding
            embedding = self.model.encode(full_text, convert_to_list=True)
            logger.debug(f"Generated semantic embedding vector of length {len(embedding)}")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {e}")
            dimension = self._get_embedding_dimension()
            return [0.0] * dimension

    def _get_embedding_dimension(self) -> int:
        if not self.model:
            return 384
        if hasattr(self.model, "get_embedding_dimension"):
            return self.model.get_embedding_dimension()
        if hasattr(self.model, "get_sentence_embedding_dimension"):
            return self.model.get_sentence_embedding_dimension()
        return 384