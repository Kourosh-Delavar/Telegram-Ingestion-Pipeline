# Telegram-Ingestion-Pipeline

A robust ETL pipeline for Telegram group chats that ingests messages, extracts text and media metadata, transforms them into searchable content, and stores both structured records and vector embeddings for retrieval-augmented generation (RAG).

## Overview

This repository is built to capture Telegram chat data from group conversations, normalize the message payloads, and persist them into two different storage layers:

- **Relational storage** for structured message records and metadata
- **Vector storage** for semantic embeddings and similarity search

The pipeline supports text, audio, photo, and document types. It is designed for use cases such as chat analytics, document search, and LLM grounding using RAG.

## Architecture

The project is organized into three core stages:

1. **Ingestion**
   - Receives Telegram updates via the Bot API
   - Normalizes incoming messages into a consistent schema
   - Supports media downloads for photos, documents, audio, and voice notes

2. **Transformation**
   - Extracts text from documents using `pdfplumber`, `python-docx`, and plain text processing
   - Performs OCR on images using `easyocr`
   - Transcribes audio via Whisper
   - Builds semantic embeddings using `sentence-transformers`

3. **Loading**
   - Writes normalized records into PostgreSQL using `psycopg2`
   - Saves vector embeddings into Weaviate for semantic retrieval
   - Uses Kafka to decouple ingestion from processing and enable scalable messaging

## Technologies Used

- **Python 3.10+** — primary runtime language
- **Telegram Bot API** (`python-telegram-bot`) — message ingestion
- **Apache Kafka** (`confluent-kafka`) — streaming layer and message orchestration
- **Apache Avro** (`confluent_kafka.schema_registry.avro`) — optional schema validation for Kafka payloads
- **PostgreSQL** (`psycopg2-binary`) — relational storage for structured message records
- **Weaviate** (`weaviate-client`) — vector database for semantic search
- **Sentence Transformers** (`sentence-transformers`) — semantic embedding generation
- **OpenAI Whisper** (`openai-whisper`) — audio transcription
- **EasyOCR** (`easyocr`) — text extraction from images
- **pdfplumber** — PDF text extraction
- **python-docx** — Word document text extraction
- **Pillow / OpenCV** — media file handling and image support
- **dotenv** (`python-dotenv`) — environment configuration management

## Key Features

- Telegram message ingestion for multiple media types
- Media file download and storage
- OCR for photo text extraction
- Audio transcription for voice and audio messages
- Document parsing for PDF, DOCX, and TXT content
- Semantic vectorization for RAG workflows
- Kafka event queue for reliable data flow
- Modular pipeline with ingest → transform → load separation

## Repository Structure

- `src/tg_ingestion_pipeline/` — main pipeline code
- `src/kafka/` — Kafka producer/consumer orchestration
- `src/tg_ingestion_pipeline/ingestion/` — Telegram ingestion handlers
- `src/tg_ingestion_pipeline/transformation/` — extraction and embedding logic
- `src/tg_ingestion_pipeline/loading/` — database and vector store loading
- `tests/` — pytest test coverage for core modules
- `docs/` — high-level documentation and architecture notes

## Setup

1. Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Configure environment variables in `.env.token`, `.env.postgres`, and `.env.weaviate` for Telegram token, PostgreSQL, and Weaviate settings.

4. Start required services:
   - PostgreSQL
   - Kafka
   - Weaviate

## Running the Pipeline

Run the package entry point:

```bash
python -m tg_ingestion_pipeline.main
```

This starts the Telegram ingestion service and processes messages through the pipeline.

## Tests

Run the unit tests with:

```bash
pytest
```

## Notes

- The current implementation stores vectors in Weaviate; Kafka is used as the event bus for decoupling ingestion and processing.
- Avro support is integrated through the Confluent Kafka Schema Registry when schema files are provided.
- If you want to extend the pipeline, add new media handlers in `ingestion/` or new transformation steps in `transformation/`.

