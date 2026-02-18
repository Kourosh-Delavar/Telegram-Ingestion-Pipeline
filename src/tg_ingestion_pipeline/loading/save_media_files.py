from typing import Optional, Dict
from telegram import Update, Message
from telegram.ext import ContextTypes


async def save_media_files(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Save media files from a Telegram message to the data directory.
    
    :param update: The Telegram update object
    :type update: Update
    :param context: The Telegram context object
    :type context: ContextTypes.DEFAULT_TYPE
    """

    msg: Optional[Message] = update.message
    if not msg:
        return
    
    # Check if the message contains a photo 
    if msg.photo:
        # Save the photo file to the data directory
        file_id  = msg.photo[-1].file_id 
        file  = await context.bot.get_file(file_id)
        extension = msg.photo[-1].mime_type.split("/")[-1].lower()

        await file.download_to_drive(f"{load_paths["photos"]}/{file_id}.{extension}")

    # Check if the message contains a document (PDF, DOCX, TXT)
    elif msg.document:
        # Save the document file to the data directory
        file_id  = msg.document.file_id 
        file  = await context.bot.get_file(file_id)
        extension = msg.document.mime_type.split("/")[-1].lower()

        await file.download_to_drive(f"{load_paths()['documents']}/{extension}/{file_id}.{extension}")
    
    # Check if the message contains an audio file (music or voice message)
    elif msg.audio or msg.voice:
        # Save the audio file to the data directory
        file_id  = msg.audio.file_id if msg.audio else msg.voice.file_id
        file  = await context.bot.get_file(file_id)
        extension = (msg.audio.mime_type if msg.audio else msg.voice.mime_type).split("/")[-1].lower()
        if extension == "ogg":
            subdir = "voice"
        else:
            subdir = "music"

        await file.download_to_drive(f"{load_paths()['audio']}/{subdir}/{file_id}.{extension}")  