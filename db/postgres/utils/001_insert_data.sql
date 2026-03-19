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
    duration_seconds,
)
VALUES (
    {message_id},
    {message_type},
    {message_timestamp},
    {chat_id},
    {content},
    {user_id},
    {username},
    {reply_to},
    {file_id},
    {mime_type},
    {file_name},
    {duration_seconds}
)
ON CONFLICT (chat_id, message_id) DO NOTHING;