import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Resource


class ResourceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, resource: Resource) -> Resource:
        self.session.add(resource)
        await self.session.flush()
        return resource

    async def get_by_stored_filename(
        self, project_uuid: uuid.UUID, stored_filename: str
    ) -> Resource | None:
        result = await self.session.execute(
            select(Resource).where(
                Resource.project_uuid == project_uuid,
                Resource.stored_filename == stored_filename,
            )
        )
        return result.scalar_one_or_none()