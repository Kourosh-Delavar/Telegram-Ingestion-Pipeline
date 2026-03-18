[Home](index.md) | [Data Schema](DATA_SCHEMA.md) | [Architecture](ARCHITECTURE.md)
# Telegram Message Data Schema

This schema defines the structure of messages ingested from Telegram. It supports multiple message types including text, audio, photos, and documents.

## Fields

### Core Message Data

| Field        | Type     | Description                                              |
| ------------ | -------- | -------------------------------------------------------- |
| `message_id` | `long`   | Unique identifier for the message (assigned by Telegram) |
| `chat_id`    | `long`   | Identifier for the chat or channel                       |
| `date`       | `string` | Timestamp of the message in ISO 8601 format              |
| `type`       | `string` | Message type: `text`, `audio`, `photo`, or `document`    |
| `content`    | `string` | Extracted text content or transcribed audio              |

### User Information

| Field       | Type             | Default | Description       |
| ----------- | ---------------- | ------- | ----------------- |
| `user_id`   | `long | null`   | `null`  | Telegram user ID  |
| `user_name` | `string | null` | `null`  | Telegram username |

### Message Relationships

| Field      | Type           | Default | Description                               |
| ---------- | -------------- | ------- | ----------------------------------------- |
| `reply_to` | `long | null` | `null`  | ID of the message this message replies to |

### Media Metadata

| Field       | Type             | Default | Description                          |
| ----------- | ---------------- | ------- | ------------------------------------ |
| `file_id`   | `string | null` | `null`  | Telegram file identifier (for media) |
| `mime_type` | `string | null` | `null`  | MIME type of the media file          |
| `file_name` | `string | null` | `null`  | Name of the document file            |

### Audio Metadata

| Field      | Type          | Default | Description                  |
| ---------- | ------------- | ------- | ---------------------------- |
| `duration` | `int | null` | `null`  | Duration of audio in seconds |

## Notes

* Fields with `null` default values are optional and may not be present depending on the message type.
* Media-related fields (`file_id`, `mime_type`, `file_name`, `duration`) are only populated for non-text messages.
* `content` may contain:

  * Raw text (for text messages)
  * Transcribed speech (for audio messages)
  * OCR-extracted text (for photo messages)
  * Text from PDF, DOCX and TXT (for document messages)
