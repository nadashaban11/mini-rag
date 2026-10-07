from fastapi import APIRouter, Depends, UploadFile, HTTPException
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
    is_valid, msg = file_service.validate_file(file.content_type,file.size)
    if not is_valid:
        raise HTTPException(
        status_code=400,
        detail=msg,
        )
    stored_filename = await file_service.save_file(
        file=file,
        project_id=project_id,
    )

    return {
        "message": "File uploaded successfully",
        "file_id": stored_filename,
    }