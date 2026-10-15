from fastapi import UploadFile

from ..core.exceptions import InvalidProjectIdError
from ..models import Resource
from ..repositories import ProjectRepository, ResourceRepository
from .file_service import FileService


class ResourceService:
    def __init__(
        self,
        file_service: FileService,
        project_repo: ProjectRepository,
        resource_repo: ResourceRepository,
    ):
        self.file_service = file_service
        self.project_repo = project_repo
        self.resource_repo = resource_repo

    async def upload(self, project_id: str, file: UploadFile) -> Resource:
        self.file_service.validate_file(file.content_type, file.size)
        if not self.file_service.validate_project_id(project_id):
            raise InvalidProjectIdError()

        project = await self.project_repo.get_or_create(project_id)
        stored_filename, size = await self.file_service.save_file(
            file=file,
            project_id=project_id,
        )

        return await self.resource_repo.add(
            Resource(
                project_uuid=project.id,
                stored_filename=stored_filename,
                original_filename=file.filename,
                content_type=file.content_type,
                size=size,
            )
        )