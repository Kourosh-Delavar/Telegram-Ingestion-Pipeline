from logging import getLogger
import logging
from typing import Any, List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Vectorizer:
    """
    Base class for vectorization of JSON data. This class provides a template for vectorization and can be extended to implement specific vectorization techniques.
    
    """
    
    def vectorize(self, data: Dict[str, Any]) -> List[float]:
        """"
        vectorize the input data and return a list of floats representing the vectorized form of the data.

        :param data: The input data to be vectorized
        :type data: Dict[str, Any]
        :return: A list of floats representing the vectorized form of the data
        """

        logger.debug(f"Vectorizing data: {data}")
        pass