[Home](index.md) | [Data Schema](DATA_SCHEMA.md) | [Architecture](ARCHITECTURE.md)

# Architecture Overview

The Telegram Ingestion Pipeline is designed to capture Telegram chat data, process it into structured text and metadata, and store it for both transactional queries and semantic retrieval.

## Core Components

1. **Telegram Ingestion**
   - `src/tg_ingestion_pipeline/ingestion/`
   - Receives messages from Telegram using the Bot API.
   - Supports text, audio, photo, and document message types.
   - Normalizes media uploads to a common message schema.

2. **Transformation**
   - `src/tg_ingestion_pipeline/transformation/`
   - Extracts text and metadata from media using OCR, speech transcription, and document parsing.
   - Builds semantic embeddings with `sentence-transformers` for RAG.
   - Prepares batches for loading into downstream storage.

3. **Loading**
   - `src/tg_ingestion_pipeline/loading/`
   - Persists structured message records into PostgreSQL.
   - Stores vectors and message metadata into Weaviate for semantic search.
   - Saves media files to local storage for replay or reprocessing.

4. **Messaging / Orchestration**
   - `src/kafka/kafka_engine.py`
   - Uses Kafka to decouple ingestion from processing, enabling scalable message handling.
   - Ensures reliable delivery and retry behavior for pipeline workers.

## Data Flow

Telegram message -> Ingestion handler -> Normalized message payload -> Transformation service -> Text extraction + embeddings -> Storage engine -> PostgreSQL + Weaviate

## External Services

- **Telegram Bot API**: source of incoming messages.
- **PostgreSQL**: persistent storage for structured message data.
- **Weaviate**: vector database for semantic retrieval and RAG.
- **Kafka**: optional queue layer for decoupling ingestion and processing.

## Deployment Notes

- The project includes a local virtual environment recommendation and can be run from source with `python -m tg_ingestion_pipeline.main`.
- Use `.env.token`, `.env.postgres`, and `.env.weaviate` to configure Telegram tokens, database URLs, and Weaviate connection details.
- If using Docker Compose, ensure all dependent services are available before starting the pipeline.

## Design Goals

- Support multiple Telegram content types with structured extraction.
- Keep storage schema flexible and compatible with RAG workflows.
- Allow easy extension for new media types or embedding models.
- Preserve raw and enriched data for both analytics and semantic search.
