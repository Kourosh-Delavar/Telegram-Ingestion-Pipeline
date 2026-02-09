import os
from dotenv import load_dotenv 
from telegram import Update 
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

# Extracting text message 
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    
    data = {
        "type": "text",
        "mesasage_id": msg.message_id,
        "content": msg.text,
        "chat_id": msg.chat_id,
        "user_id": msg.from_user.id if msg.from_user else None,
        "user_name": msg.from_user.username if msg.from_user else None,
        "date": msg.date.isoformat(),
        "reply_to": msg.reply_to_message.message_id if msg.reply_to_message else None
    }

    print(data)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    
    data = {
        "type": "photo",
        "message_id": msg.message_id,
        "content": [photo.file_id for photo in msg.photo],
        "chat_id": msg.chat_id,
        "user_id": msg.from_user.id if msg.from_user else None,
        "user_name": msg.from_user.username if msg.from_user else None,
        "date": msg.date.isoformat(),
        "reply_to": msg.reply_to_message.message_id if msg.reply_to_message else None
    }

    print(data)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.run_polling()