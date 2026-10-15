from ..core.exceptions import InvalidProjectIdError, ProjectNotFoundError
from ..repositories import ProjectRepository
from .file_service import FileService


class ProjectService:
    def __init__(self, file_service: FileService, project_repo: ProjectRepository):
        self.file_service = file_service
        self.project_repo = project_repo

    async def delete(self, project_id: str) -> None:
        if not self.file_service.validate_project_id(project_id):
            raise InvalidProjectIdError()

        project = await self.project_repo.get_by_project_id(project_id)
        if project is None:
            raise ProjectNotFoundError()

        await self.project_repo.delete(project.id)
        self.file_service.delete_project_directory(project_id)