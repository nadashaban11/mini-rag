from fastapi import APIRouter, Depends, UploadFile

from mini_rag.api.dependencies import get_file_service, get_process_service
from mini_rag.schemas.process import ProcessRequest
from mini_rag.services.file_service import FileService
from mini_rag.services.process_service import ProcessService



router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"],
)

@router.post("/upload/{project_id}")
async def upload_data(
    project_id: str,
    file: UploadFile,
    file_service: FileService = Depends(get_file_service),
):
    file_service.validate_file(file.content_type, file.size)
    stored_filename = await file_service.save_file(
        file=file,
        project_id=project_id,
    )

    return {
        "message": "File uploaded successfully",
        "file_id": stored_filename,
    }


@router.post("/process/{project_id}")
def process_data(
    project_id: str,
    request: ProcessRequest,
    process_service: ProcessService = Depends(get_process_service),
):
    chunks = process_service.process_file(
        project_id=project_id,
        file_id=request.file_id,
        chunk_size=request.chunk_size,
        overlap_size=request.overlap_size,
    )
    return {
        "message": "File processed successfully",
        "chunks_count": len(chunks),
        "chunks": [
            {"content": c.page_content, "metadata": c.metadata} for c in chunks
        ],
    }