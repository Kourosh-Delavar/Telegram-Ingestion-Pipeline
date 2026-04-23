# Docker Deployment Guide

## Complete Setup for Telegram Ingestion Pipeline with Docker

This guide shows how to run all services (Kafka, PostgreSQL, Weaviate) using Docker Compose.

### Prerequisites

- Docker installed and running
- WSL 2 with Docker Desktop integration (on Windows)
- Python 3.10+ (for running the bot locally)

### Quick Start

#### 1. Start All Services

```bash
cd /home/kourosh/projects/Telegram-Ingestion-Pipeline
docker-compose up -d
```

This starts:
- **Kafka** (port 9092) - Message broker
- **PostgreSQL** (port 5432) - Relational database
- **Weaviate** (port 8080) - Vector database

#### 2. Verify Services are Running

```bash
# Check all containers
docker-compose ps

# Expected output:
# NAME        STATUS      PORTS
# kafka       Up (healthy)  0.0.0.0:9092->9092/tcp
# postgres    Up (healthy)  0.0.0.0:5432->5432/tcp
# weaviate    Up (healthy)  0.0.0.0:8080->8080/tcp
```

#### 3. Run the Bot (from your host machine)

```bash
cd /home/kourosh/projects/Telegram-Ingestion-Pipeline
source .venv/bin/activate
python3 src/tg_ingestion_pipeline/main.py
```

### Service Connections

The bot connects to services using **Docker service names** (only within the Docker network):

| Service | Docker URL | Host URL | Port |
|---------|-----------|----------|------|
| Kafka | kafka:9092 | localhost:9092 | 9092 |
| PostgreSQL | postgres:5432 | localhost:5432 | 5432 |
| Weaviate | weaviate:8080 | localhost:8080 | 8080 |

**Note**: When running the bot on the host machine (not in a container), use `localhost` URLs. The environment files already handle this.

### Environment Configuration

**`.env.postgres`**
```bash
POSTGRES_USER=ingestion_user
POSTGRES_PASSWORD=secure_ingestion_password_2024
POSTGRES_DB=telegram_db
POSTGRES_HOST=postgres          # Docker service name
POSTGRES_PORT=5432
```

**`.env.weaviate`**
```bash
WEAVIATE_URL=http://weaviate:8080    # Docker service name
WEAVIATE_API_KEY=                     # Anonymous access enabled
```

**`.env.kafka`**
```bash
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_SCHEMA_REGISTRY_URL=http://schema-registry:8081
```

### Docker Network

All services are connected via a custom bridge network: `ingestion_network`
- Services can communicate using their container names
- Host machine can access services via `localhost:port`

### Health Checks

Each service has health checks configured:
- Kafka: Broker API check every 10s
- PostgreSQL: Database connection check every 10s
- Weaviate: Ready endpoint check every 10s

```bash
# View health status
docker-compose ps

# View logs for a specific service
docker-compose logs postgres
docker-compose logs weaviate
docker-compose logs kafka
```

### Stopping Services

```bash
# Stop all containers (keep volumes)
docker-compose stop

# Stop and remove containers (keep volumes)
docker-compose down

# Stop, remove containers AND volumes (WARNING: deletes data)
docker-compose down -v
```

### Troubleshooting

**Kafka not connecting:**
```bash
# Check Kafka logs
docker-compose logs kafka

# Test connection from host
nc -zv localhost 9092
```

**PostgreSQL not accessible:**
```bash
# Check logs
docker-compose logs postgres

# Verify port
docker-compose ps postgres
```

**Weaviate connection failed:**
```bash
# Check Weaviate logs
docker-compose logs weaviate

# Test health endpoint
curl http://localhost:8080/v1/.well-known/ready
```

### Running Bot Inside Docker (Optional)

To run the bot inside a Docker container (advanced):

1. Create a Dockerfile for the bot
2. Add a service in docker-compose.yml
3. Set environment variables to use internal Docker service names

### Data Persistence

All data is persisted in Docker volumes:
- `kafka_data` - Kafka broker state
- `postgres_data` - PostgreSQL database
- `weaviate_data` - Weaviate vector index

Volumes survive container restarts but are deleted with `docker-compose down -v`.

### Next Steps

1. Start Docker services: `docker-compose up -d`
2. Wait for health checks to pass (monitor with `docker-compose ps`)
3. Update BOT_TOKEN in `.env.token`
4. Run the bot: `python3 src/tg_ingestion_pipeline/main.py`
5. Send messages to your Telegram bot to test the pipeline

### Monitoring

View real-time logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f postgres
docker-compose logs -f weaviate
docker-compose logs -f kafka
```

### Database Inspection

Connect to PostgreSQL:
```bash
psql -h localhost -U ingestion_user -d telegram_db -W

# Password: secure_ingestion_password_2024
```

Query messages:
```sql
SELECT * FROM messages LIMIT 10;
```

### Weaviate Inspection

Visit Weaviate Console:
```
http://localhost:8080/v1/graphql
```

Query Telegram messages:
```graphql
{
  Get {
    TelegramMessage {
      message_id
      content
      username
    }
  }
}
```
