import logging
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from .utils.base_msg import extract_base_message_data
from .utils.mime_type_converter import mime_type_to_extension
from .utils.file_cleaner import delete_media_file
from tg_ingestion_pipeline.ingestion.tools.document_tools.pdf_extractor import extract_text_from_pdf
from tg_ingestion_pipeline.ingestion.tools.document_tools.docx_extractor import extract_text_from_docx
from tg_ingestion_pipeline.ingestion.tools.document_tools.txt_extractor import extract_text_from_txt_file
from tg_ingestion_pipeline.ingestion.services.media_downloader import download_document
from tg_ingestion_pipeline.ingestion.services.message_publisher import publish_extracted_message


logger = logging.getLogger(__name__)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle document messages.
    
    :param update: Telegram Update object
    :type update: Update
    :param context: Telegram Context object
    :type context: ContextTypes.DEFAULT_TYPE
    :return: None
    """


    try:
        msg = update.message
        if not msg or not msg.document:
            logger.warning("Received document message without content")
            return None
        
        file_id: str = msg.document.file_id
        logger.info(f"Document file_id: {file_id}")
        mime_type: Optional[str] = msg.document.mime_type.lower() if msg.document.mime_type else None
        logger.info(f"Document mime_type: {mime_type}")

        file_extension = mime_type_to_extension(mime_type, media_type="document")        

        # Scan the document
        file_path = None
        try:
            file_path = await download_document(context, file_id=file_id, mime_type=mime_type)
            if "pdf" in file_extension:
                extracted_content = extract_text_from_pdf(file_path)
            elif "docx" in file_extension:
                extracted_content = extract_text_from_docx(file_path)
            elif "txt" in file_extension:
                extracted_content = extract_text_from_txt_file(file_path)
            else:
                extracted_content = None
        except Exception as e:
            logger.error(f"Error during document scanning: {e}")
            extracted_content = None

        if extracted_content is not None:
            data = {
                "file_id": file_id,
                "type": "document",
                "content": extracted_content,
                "file_name": msg.document.file_name,
                "mime_type": msg.document.mime_type,
                **extract_base_message_data(msg),
            }
            logger.info(f"Document message received from {msg.from_user.username}")
        else:
            data = {
                "file_id": file_id,
                "type": "document",
                "content": file_id,
                "file_name": msg.document.file_name,
                "mime_type": msg.document.mime_type,
                **extract_base_message_data(msg),
            }
            logger.info(f"Document message received from {msg.from_user.username} without extracted content. Using file_id as content.")

        publish_extracted_message(key=file_id, data=data)
        
        # Delete media file after successful extraction and Kafka message sending
        if file_path is not None:
            delete_media_file(file_path)
    except Exception as e:
        logger.error(f"Error handling document message: {e}")
        return None