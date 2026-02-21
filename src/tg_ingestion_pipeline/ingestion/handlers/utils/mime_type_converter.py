from typing import Optional


# MIME type to file extension mappings
AUDIO_MIME_TYPES = {
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/ogg": "ogg",
    "audio/wav": "wav",
    "audio/webm": "webm",
    "audio/m4a": "m4a",
    "audio/aac": "aac",
    "audio/flac": "flac",
    "audio/opus": "opus",
}

DOCUMENT_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/msword": "doc",
    "text/plain": "txt",
    "text/html": "html",
    "application/vnd.ms-excel": "xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/rtf": "rtf",
}

PHOTO_MIME_TYPES = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/bmp": "bmp",
    "image/tiff": "tiff",
}


def mime_type_to_extension(
    mime_type: Optional[str],
    media_type: str = "audio"
) -> str:
    """
    Convert MIME type to file extension.
    
    :param mime_type: MIME type string 
    :param media_type: Type of media ('audio', 'document', 'photo')
    :return: File extension without the dot 
    """


    if not mime_type:
        # Return default extensions based on media type
        defaults = {
            "audio": "wav",
            "document": "txt",
            "photo": "jpg",
        }
        return defaults.get(media_type, "bin")
    
    mime_map = {
        "audio": AUDIO_MIME_TYPES,
        "document": DOCUMENT_MIME_TYPES,
        "photo": PHOTO_MIME_TYPES,
    }
    
    selected_map = mime_map.get(media_type, {})
    return selected_map.get(mime_type.lower(), "bin")
