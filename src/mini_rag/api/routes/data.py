from fastapi import APIRouter, Depends, UploadFile

from mini_rag.api.dependencies import (
    get_process_service,
    get_project_service,
    get_resource_service,
)
from mini_rag.schemas.process import ProcessRequest
from mini_rag.services.process_service import ProcessService
from mini_rag.services.project_service import ProjectService
from mini_rag.services.resource_service import ResourceService

router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"],
)


@router.post("/upload/{project_id}")
async def upload_data(
    project_id: str,
    file: UploadFile,
    resource_service: ResourceService = Depends(get_resource_service),
):
    resource = await resource_service.upload(project_id, file)
    return {
        "message": "File uploaded successfully",
        "file_id": resource.stored_filename,
    }


@router.post("/process/{project_id}")
async def process_data(
    project_id: str,
    request: ProcessRequest,
    process_service: ProcessService = Depends(get_process_service),
):
    chunks_count = await process_service.process_file(
        project_id=project_id,
        file_id=request.file_id,
        chunk_size=request.chunk_size,
        overlap_size=request.overlap_size,
    )
    return {
        "message": "File processed successfully",
        "chunks_count": chunks_count,
    }


@router.delete("/{project_id}/files/{file_id}", status_code=204)
async def delete_file(
    project_id: str,
    file_id: str,
    resource_service: ResourceService = Depends(get_resource_service),
):
    await resource_service.delete(project_id, file_id)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service),
):
    await project_service.delete(project_id)