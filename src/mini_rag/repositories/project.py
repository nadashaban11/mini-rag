from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_project_id(self, project_id: str) -> Project | None:
        result = await self.session.execute(
            select(Project).where(Project.project_id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, project_id: str) -> Project:
        project = await self.get_by_project_id(project_id)
        if project is None:
            project = Project(project_id=project_id)
            self.session.add(project)
            await self.session.flush()
        return project