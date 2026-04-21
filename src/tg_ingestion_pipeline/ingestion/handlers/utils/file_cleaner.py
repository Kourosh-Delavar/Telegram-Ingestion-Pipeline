import logging
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


def delete_media_file(file_path: Optional[Path]) -> bool:
    """
    Delete a media file after successful extraction.
    
    :param file_path: Path to the media file to delete
    :type file_path: Optional[Path]
    :return: True if file was deleted successfully, False otherwise
    """
    
    if not file_path:
        logger.warning("Attempted to delete None file path")
        return False
    
    try:
        file_path = Path(file_path)
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Successfully deleted media file: {file_path}")
            return True
        else:
            logger.warning(f"Media file does not exist, skipping deletion: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error deleting media file {file_path}: {type(e).__name__}: {e}")
        return False
