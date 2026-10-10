# mini-rag

A small FastAPI service for the ingestion side of a RAG pipeline.
It uploads files into project-scoped folders, then loads and splits them into chunks ready for embedding.

## Features
- Upload files per project: `POST /api/v1/data/upload/{project_id}`
- Process an uploaded file (load + chunk): `POST /api/v1/data/process/{project_id}`
- Supported types for processing: `.txt` and `.pdf`
- Validation of file type and size (configurable)
- Safe filenames: sanitized and prefixed with a random key to avoid collisions
- Consistent JSON errors via domain exceptions
- Health check: `GET /api/v1/health`

## Requirements
- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Setup
```bash
uv sync
cp .env.example .env
```

## Configuration (`.env`)
| Variable | Description | Example |
|---|---|---|
| `FILE_ALLOWED_TYPES` | Allowed MIME types (JSON list) | `["text/plain","application/pdf"]` |
| `FILE_MAX_SIZE` | Max upload size in MB | `10` |
| `FILE_DEFAULT_CHUNK_SIZE` | Bytes read per chunk while saving | `512000` |

## Run
```bash
uv run fastapi dev src/mini_rag/main.py
```
Interactive docs: http://localhost:8000/docs

## API

### Upload a file
`POST /api/v1/data/upload/{project_id}` (multipart, field name `file`)

`project_id` accepts letters, digits, `_` and `-` only.

Success:
```json
{ "message": "File uploaded successfully", "file_id": "aB3xK9pQ_report.pdf" }
```

| Status | Meaning |
|---|---|
| 400 | Invalid project ID |
| 413 | File too large |
| 415 | Unsupported file type |

Files are stored in `assets/files/{project_id}/`.

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

Success:
```json
{
  "message": "File processed successfully",
  "chunks_count": 22,
  "chunks": [
    { "content": "...", "metadata": { "source": "...", "page": 0 } }
  ]
}
```

| Status | Meaning |
|---|---|
| 400 | Invalid project ID |
| 404 | File not found in this project |
| 415 | File type cannot be processed |
| 422 | Invalid request body, or no content could be extracted |


## Structure
```
src/mini_rag/
├── api/        # routers, dependencies
├── core/       # settings + exceptions
└── services/   # FileService (validation, storage), ProcessService (load, chunk)
└── Schemas/    # request models (pydantic)
```

## Roadmap
- [x] Upload files per project
- [x] Process uploaded files (load + chunk)
- [ ] Embeddings + vector store
- [ ] Retrieval + answer generation