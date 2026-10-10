from fastapi import APIRouter, Depends, UploadFile

from mini_rag.api.dependencies import get_file_service
from mini_rag.services.file_service import FileService



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