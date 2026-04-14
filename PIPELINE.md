# Telegram Ingestion Pipeline — Complete Data Flow

This is the unified Telegram-to-relational-DB and vector-DB ingestion pipeline. Once `python -m tg_ingestion_pipeline.main` runs, it automatically:

## Flow Overview

1. **Telegram Ingestion** (via bot handlers)
   - Polls Telegram group chats
   - Handlers extract: text, photos (OCR), documents (PDF/DOCX/TXT), audio (transcription)
   - Messages sent to Kafka topic `extracted-data` with base metadata

2. **Kafka Message Distribution**
   - KafkaOrchestrator produces messages to `extracted-data` topic

3. **Background Processing Pipeline** (TelegramDataPipeline)
   - Asynchronous thread subscribes to `extracted-data` topic
   - For each message:
     a. Normalizes fields to relational schema
     b. Inserts into PostgreSQL `messages` table (source of truth)
     c. Vectorizes message content via Vectorizer
     d. Stores embedding + metadata in Weaviate

4. **Databases**
   - **PostgreSQL**: Relational storage for all message attributes (source of truth)
   - **Weaviate**: Vector search index over message embeddings (main purpose for RAG)

## Embedding Model for RAG

The pipeline uses **sentence-transformers** with the `all-MiniLM-L6-v2` model to generate high-quality semantic embeddings (384 dimensions) optimized for:

- **Semantic similarity search** — Find messages with similar meaning, not just keywords
- **LLM integration** — Embeddings compatible with retrieval-augmented generation workflows
- **Context preservation** — Combines message content with metadata (user, file type, etc.)

The Vectorizer automatically handles:
- Text tokenization and encoding
- Metadata enrichment for better context
- Fallback handling for empty content
- Model caching for performance

## RAG Usage Example

```python
# Query similar messages using semantic search
from weaviate_client import WeaviateClient

client = WeaviateClient()
results = client.query.nearText(
    concepts=["questions about machine learning"],
    class_name="TelegramMessage"
).do()
```

## Key Modules

| Module | Purpose |
|---------|---------|
| [src/kafka/kafka_engine.py](src/kafka/kafka_engine.py) | KafkaOrchestrator — produce/consume Kafka messages |
| [src/tg_ingestion_pipeline/main.py](src/tg_ingestion_pipeline/main.py) | Telegram bot entry point; launches background pipeline |
| [src/tg_ingestion_pipeline/transformation/processing/pipeline.py](src/tg_ingestion_pipeline/transformation/processing/pipeline.py) | TelegramDataPipeline — main async processor |
| [src/tg_ingestion_pipeline/loading/db/insert_db.py](src/tg_ingestion_pipeline/loading/db/insert_db.py) | insert_message() — PostgreSQL writer |
| [src/tg_ingestion_pipeline/loading/vectordb/weaviate_client.py](src/tg_ingestion_pipeline/loading/vectordb/weaviate_client.py) | WeaviateClient — vector DB upsert |
| [src/tg_ingestion_pipeline/transformation/embeddings/embedding_model.py](src/tg_ingestion_pipeline/transformation/embeddings/embedding_model.py) | Vectorizer — semantic embeddings using sentence-transformers for RAG |
| [src/tg_ingestion_pipeline/transformation/processing/data_loader.py](src/tg_ingestion_pipeline/transformation/processing/data_loader.py) | load_data_from_kafka() — Kafka consumer generator |

## Setup & Deployment

### Prerequisites

- Python 3.10+
- PostgreSQL database (with schema from [db/postgres/schema/001_create_tables.sql](db/postgres/schema/001_create_tables.sql))
- Kafka cluster (localhost:9092 by default)
- Weaviate instance (http://localhost:8080 by default)

### Environment Variables

Create the following environment files in the project root:

**`.env.token`** (Telegram bot token):
```
BOT_TOKEN=your_telegram_bot_token
```

**`.env.postgres`** (PostgreSQL connection):
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=telegram_ingestion
```

**`.env.weaviate`** (Weaviate connection):
```
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=  # Leave empty if no auth
```

### Installation

```bash
cd Telegram-Ingestion-Pipeline
pip install -e .
```

This installs the pipeline with dependencies including `weaviate-client`.

### Running the Pipeline

```bash
python -m tg_ingestion_pipeline.main
```

The application will:
1. Initialize the PostgreSQL schema
2. Start the background TelegramDataPipeline thread
3. Begin polling Telegram for messages
4. Automatically consume, process, and persist messages in real-time

### Logging

All modules use structured logging at INFO level. Pipeline logs include:
- Kafka message consumption
- PostgreSQL insert results
- Weaviate vector storage operations
- Embedding generation

## Coding Conventions Applied

- **Logging**: Context-aware logger per module using `logging.getLogger(__name__)`
- **Type hints**: Full type annotations for all public functions
- **Error handling**: Try-except with logging fallbacks; no silent failures
- **Path management**: `pathlib.Path` for SQL file resolution
- **Config management**: Environment variables via `python-dotenv`
- **Async**: Background thread for pipeline via `threading.Thread`
- **Docstrings**: Module and function docstrings follow NumPy/Google style

## Architecture Benefits

 **Decoupled**: Telegram ingestion separate from backend processing  
 **Scalable**: Kafka broker decouples producers/consumers  
 **Redundant**: PostgreSQL = source of truth; Weaviate = searchable index  
 **Observable**: Comprehensive request/response logging  
 **Extensible**: Easy to add new message types or vectorization strategies  

