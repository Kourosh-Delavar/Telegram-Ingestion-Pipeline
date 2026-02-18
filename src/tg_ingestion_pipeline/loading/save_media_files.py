from typing import Dict
from telegram import Update, Message
from telegram.ext import ContextTypes
import json

async def save_media_files(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Save media files from a Telegram message to the data directory.
    
    :param update: The Telegram update object
    :type update: Update
    :param context: The Telegram context object
    :type context: ContextTypes.DEFAULT_TYPE
    """

    # Loading paths from JSON file
    try:
        with open("test/loading_test/test_saving_paths.json", "r") as f:
                paths: Dict[str, str] = json.load(f)
    except FileNotFoundError:
        print("Error: test_saving_paths.json not found.")
        return # TODO: replace with logging and raise an exception

    msg: Optional[Message] = update.message
    if not msg:
        return
    
    # Check if the message contains a photo 
    if msg.photo:
        # Save the photo file to the data directory
        file_id  = msg.photo[-1].file_id 
        file  = await context.bot.get_file(file_id)
        extension = msg.photo[-1].mime_type.split("/")[-1].lower()

        await file.download_to_drive(f"{paths['photos']}/{file_id}.{extension}")

    # Check if the message contains a document (PDF, DOCX, TXT)
    elif msg.document:
        # Save the document file to the data directory
        file_id  = msg.document.file_id 
        file  = await context.bot.get_file(file_id)
        extension = msg.document.mime_type.split("/")[-1].lower()

        await file.download_to_drive(f"{paths['documents'][extension]}/{file_id}.{extension}")
    
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

        await file.download_to_drive(f"{paths['audio'][subdir]}/{file_id}.{extension}")  