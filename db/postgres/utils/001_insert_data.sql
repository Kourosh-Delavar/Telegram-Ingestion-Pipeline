INSERT INTO messages (
    message_id,
    message_type,
    message_timestamp,
    chat_id,
    content,
    user_id,
    username,
    reply_to,
    file_id,
    mime_type,
    file_name,
    duration_seconds
)
VALUES (
    %(message_id)s,
    %(message_type)s,
    %(message_timestamp)s,
    %(chat_id)s,
    %(content)s,
    %(user_id)s,
    %(username)s,
    %(reply_to)s,
    %(file_id)s,
    %(mime_type)s,
    %(file_name)s,
    %(duration_seconds)s
)
ON CONFLICT (chat_id, message_id) DO NOTHING;