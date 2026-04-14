[Home](index.md) | [Data Schema](DATA_SCHEMA.md) | [Architecture](ARCHITECTURE.md)

# Telegram Ingestion Pipeline Documentation

This documentation provides a high-level overview of the pipeline, the Telegram message data schema, and architecture details for deployment and extension.

## Contents

- [Data Schema](DATA_SCHEMA.md): definition of the ingested message structure.
- [Architecture](ARCHITECTURE.md): component architecture, data flow, and service dependencies.

## Purpose

The pipeline collects Telegram messages, extracts text and media metadata, and stores both relational data and vector embeddings for retrieval-augmented generation (RAG) use cases.
