# mini-rag

A small FastAPI service for the ingestion side of a RAG pipeline.
It uploads files into project-scoped folders, loads and splits them into chunks, and stores resources and chunks in Postgres, ready for embedding.

## Features
- Upload files per project: `POST /api/v1/data/upload/{project_id}`
- Process an uploaded file (load + chunk + store): `POST /api/v1/data/process/{project_id}`
- Delete a file: `DELETE /api/v1/data/{project_id}/files/{file_id}`
- Delete a whole project: `DELETE /api/v1/data/{project_id}`
- Supported types for processing: `.txt` and `.pdf`
- Projects, resources, and chunks persisted in Postgres
- Reprocessing a file replaces its old chunks
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

To stop it:
```bash
docker compose down
```

## Configuration (`.env`)
| Variable | Description | Example |
|---|---|---|
| `FILE_ALLOWED_TYPES` | Allowed MIME types (JSON list) | `["application/pdf","text/plain"]` |
| `FILE_MAX_SIZE` | Max upload size in MB | `10` |
| `FILE_DEFAULT_CHUNK_SIZE` | Bytes read per chunk while saving | `524288` |
| `POSTGRES_USER` | Postgres username (also used by the Docker container) | `postgres` |
| `POSTGRES_PASSWORD` | Postgres password (also used by the Docker container) | `password` |
| `POSTGRES_DB` | Database name, created automatically on first start | `mini_rag` |

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

The file is loaded and split, then the chunks are saved in Postgres. If the file was processed before, its old chunks are deleted first.

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

## Structure
```
├── api/            # routers (health, data), dependencies
├── core/           # settings, database, exceptions
├── models/         # SQLAlchemy models (Project, Resource, Chunk)
├── repositories/   # DB access (Project, Resource, Chunk)
├── schemas/        # request models (pydantic)
└── services/       # FileService (validation, storage), ResourceService,
                    # ProjectService, ProcessService (load, chunk, store)
```

## Roadmap
- [x] Upload files per project
- [x] Process uploaded files (load + chunk)
- [x] Persist projects, resources, and chunks in Postgres
- [x] Delete files and projects
- [ ] Embeddings + vector store
- [ ] Retrieval + answer generation