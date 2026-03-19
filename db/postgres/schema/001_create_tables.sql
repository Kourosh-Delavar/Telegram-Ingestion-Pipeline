CREATE TABLE IF NOT EXISTS messages (
    -- Core fields
    message_id BIGINT PRIMARY KEY,
    message_type VARCHAR(50) NOT NULL,
    message_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    chat_id BIGINT NOT NULL,
    content TEXT,

    -- User info
    user_id BIGINT,
    username VARCHAR(255),

    -- Message relationships
    reply_to BIGINT,

    -- Media metadata
    file_id VARCHAR(255),
    mime_type VARCHAR(100),
    file_name VARCHAR(255),

    -- Audio metadata (only for audio messages)
    duration_seconds INTEGER,

    -- Primary key
    PRIMARY KEY (chat_id, message_id)
);