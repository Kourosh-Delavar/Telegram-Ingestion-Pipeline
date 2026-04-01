from typing import AsyncGenerator, Dict, Any, Generator
import logging 

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataFlattener:
    """
    DataFlattener flattens nested data structures to simplify their use in downstream processes.
    The flattened data is mainly used as a context component for vector database operations.
    """

    def _flatten_dict(self, d: AsyncGenerator[Dict[str, Any], None], parent_key):
        """
        Flatten a nested dictionary by concatenating keys with a separator.
        """
        pass

    def flatten_data(self, data: AsyncGenerator[Dict[str, Any], None]) -> Generator[str, None, None]:
        """
        Flatten nested data structures in the deserialized messages.

        :param data: Generator yielding deserialized messages
        :type data: Generator[Dict[str, Any], None, None]
        :return: Generator[str, None, None]
        """
        pass