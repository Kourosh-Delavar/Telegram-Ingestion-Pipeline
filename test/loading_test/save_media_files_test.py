from typing import Dict
from tg_ingestion_pipeline.loading.save_media_files import save_media_files
import json 

async def test_save_media_files() -> None:
    """
    Test the save_media_files function to ensure it correctly saves media files from Telegram messages.

    :return: None
    """

    # Load the saving paths from the JSON file
    with open("test/loading_test/test_saving_paths.json", "r") as f:
        paths: Dict[str, str] = json.load(f)