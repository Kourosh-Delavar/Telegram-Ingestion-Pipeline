from typing import Dict, Any, Generator
import logging 

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataFlattener:
    """
    DataFlattener is a class responsible for flattening nested data structures in the deserialized messages.
    """

    def __init__(self):
        pass        

    def _flatten_dict(self, d: Dict[str, Any], parent_key):
        """
        Flatten a nested dictionary by concatenating keys with a separator.
        """
        pass

    def flatten_data(self, data: Generator[Dict[str, Any], None, None]) -> Generator[str, None, None]:
        """
        Flatten nested data structures in the deserialized messages.

        :param data: Generator yielding deserialized messages
        :type data: Generator[Dict[str, Any], None, None]
        :return: Generator[str, None, None]
        """
        pass