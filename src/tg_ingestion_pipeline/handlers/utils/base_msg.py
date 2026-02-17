from typing import Any, Dict, Optional


def extract_user_info(user) -> Dict[str, Any]:
    """
    Extract user information from a User object.

    args:
        user: Telegram User object
    """

    return {
        "user_id": user.id if user else None,
        "user_name": user.username if user else None,
    }


def extract_base_message_data(msg) -> Dict[str, Any]:
    """
    Extract common message data fields.
    
    args:
        msg: Telegram Message object
    """
    
    return {
        "message_id": msg.message_id,
        "chat_id": msg.chat_id,
        "date": msg.date.isoformat(),
        "reply_to": msg.reply_to_message.message_id if msg.reply_to_message else None,
        **extract_user_info(msg.from_user)
    }