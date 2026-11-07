# mini-rag

A small FastAPI service for the ingestion side of a RAG pipeline.
It uploads files into project-scoped folders, loads and splits them into chunks, embeds the chunks in batches, and stores resources and chunks (with vectors) in Postgres using pgvector.

## Features
- Upload files per project: `POST /api/v1/data/upload/{project_id}`
- Process an uploaded file (load + chunk + embed + store): `POST /api/v1/data/process/{project_id}`
- Delete a file: `DELETE /api/v1/data/{project_id}/files/{file_id}`
- Delete a whole project: `DELETE /api/v1/data/{project_id}`
- Supported types for processing: `.txt` and `.pdf`
- Projects, resources, and chunks persisted in Postgres
- Chunk embeddings generated in batches via the configured LLM provider
- Embeddings stored in a pgvector `vector(2048)` column
- Reprocessing a file replaces its old chunks and embeddings
- Validation of file type and size (configurable)
- Safe filenames: sanitized and prefixed with a random key to avoid collisions
- Consistent JSON errors via domain exceptions
- Health check: `GET /api/v1/health`

## Requirements
- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- [Docker](https://docs.docker.com/get-docker/) (for PostgreSQL with pgvector)

## Setup
```bash
uv sync
cp .env.example .env
```

## Database
Start Postgres (uses `pgvector/pgvector:pg16`) from the folder containing `docker-compose.yml`:
```bash
docker compose up -d
```
It reads `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` from the root `.env`, and is exposed on `localhost:5433`. Data is persisted in `./pgdata`.

Apply migrations (this also enables the `vector` extension):
```bash
uv run alembic upgrade head
```

To stop it:
```bash
docker compose down
```

## Configuration (`.env`)

### Files and database
| Variable | Description | Example |
|---|---|---|
| `FILE_ALLOWED_TYPES` | Allowed MIME types (JSON list) | `["application/pdf","text/plain"]` |
| `FILE_MAX_SIZE` | Max upload size in MB | `10` |
| `FILE_DEFAULT_CHUNK_SIZE` | Bytes read per chunk while saving | `524288` |
| `POSTGRES_USER` | Postgres username (also used by the Docker container) | `postgres` |
| `POSTGRES_PASSWORD` | Postgres password (also used by the Docker container) | `password` |
| `POSTGRES_DB` | Database name, created automatically on first start | `mini_rag` |

### LLM and embeddings
| Variable | Description | Example |
|---|---|---|
| `GENERATION_BACKEND` | Generation provider | `openai` |
| `EMBEDDING_BACKEND` | Embedding provider | `openai` |
| `OPENAI_API_KEY` | API key for the OpenAI-compatible provider | — |
| `OPENAI_BASE_URL` | Base URL for the provider; leave blank for OpenAI | — |
| `GENERATION_MODEL_ID` | Chat model used for answer generation | — |
| `EMBEDDING_MODEL_ID` | Embedding model used for chunks and queries | — |
| `EMBEDDING_SIZE` | Vector dimension; must match the model **and** the DB column | `2048` |
| `EMBEDDING_BATCH_SIZE` | Number of texts sent per embedding request | `50` |
| `GENERATION_DEFAULT_MAX_TOKENS` | Default max output tokens | `1000` |
| `GENERATION_DEFAULT_TEMPERATURE` | Default sampling temperature | `0.1` |

## Run
```bash
uv run fastapi dev src/mini_rag/main.py
```
Interactive docs: http://localhost:8000/docs

## API

### Upload a file
`POST /api/v1/data/upload/{project_id}` (multipart, field name `file`)

`project_id` accepts letters, digits, `_` and `-` only. The project is created automatically on first upload.

Success:
```json
{ "message": "File uploaded successfully", "file_id": "aB3xK9pQ_report.pdf" }
```

| Status | Meaning |
|---|---|
| 400 | Invalid project ID |
| 413 | File too large |
| 415 | Unsupported file type |

Files are stored in `assets/files/{project_id}/`, and a resource record is saved in Postgres.

### Process a file
`POST /api/v1/data/process/{project_id}` (JSON)

Request:
```json
{
  "file_id": "aB3xK9pQ_report.pdf",
  "chunk_size": 1000,
  "overlap_size": 200
}
```

| Field | Default | Rules |
|---|---|---|
| `file_id` | required | the `file_id` returned by upload |
| `chunk_size` | `1000` | must be greater than 0 |
| `overlap_size` | `200` | must be >= 0 and smaller than `chunk_size` |

The file is loaded and split, the chunks are embedded in batches, then the chunks and vectors are saved in Postgres. If the file was processed before, its old chunks are deleted first — but only after embedding succeeds, so a provider failure leaves the previous chunks intact.

Success:
```json
{
  "message": "File processed successfully",
  "chunks_count": 22
}
```

| Status | Meaning |
|---|---|
| 400 | Invalid project ID |
| 404 | Project or file not found |
| 415 | File type cannot be processed |
| 422 | Invalid request body, or no content could be extracted |
| 502 | Embedding provider request failed |

### Delete a file
`DELETE /api/v1/data/{project_id}/files/{file_id}`

Removes the resource (and its chunks) from Postgres and the file from storage.

| Status | Meaning |
|---|---|
| 204 | Deleted |
| 400 | Invalid project ID |
| 404 | Project or file not found |

### Delete a project
`DELETE /api/v1/data/{project_id}`

Removes the project and its data from Postgres, and deletes its storage folder.

| Status | Meaning |
|---|---|
| 204 | Deleted |
| 400 | Invalid project ID |
| 404 | Project not found |

## Embeddings
- `EmbeddingService` splits texts into batches (`EMBEDDING_BATCH_SIZE`) and validates every returned vector's length against `EMBEDDING_SIZE`.
- Vectors are stored in `chunks.chunk_embedding`, a nullable `vector(2048)` column.
- Changing `EMBEDDING_MODEL_ID` to a model with a different dimension requires a migration and reprocessing existing files.

## Tests
```bash
uv run python -m unittest discover -s tests -v
```

## Structure
```
├── api/            # routers (health, data), dependencies
├── core/           # settings, database, exceptions
├── llm/            # LLMInterface, OpenAI provider, factory, enums
├── models/         # SQLAlchemy models (Project, Resource, Chunk)
├── repositories/   # DB access (Project, Resource, Chunk)
├── schemas/        # request models (pydantic)
├── services/       # FileService, ResourceService, ProjectService,
│                   # ProcessService (load, chunk, embed), EmbeddingService
├── migrations/     # Alembic migrations (pgvector extension + schema)
└── tests/          # unittest suite
```

## Roadmap
- [x] Upload files per project
- [x] Process uploaded files (load + chunk)
- [x] Persist projects, resources, and chunks in Postgres
- [x] Delete files and projects
- [x] Embeddings + vector store
- [ ] Retrieval + answer generation