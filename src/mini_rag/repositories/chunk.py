import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Chunk


class ChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, chunk: Chunk) -> Chunk:
        self.session.add(chunk)
        await self.session.flush()
        return chunk

    async def add_many(self, chunks: list[Chunk]) -> int:
        self.session.add_all(chunks)
        await self.session.flush()
        return len(chunks)

    async def get_by_project_id(self, chunk_id: str) -> Chunk | None:
        result = await self.session.execute(
            select(Chunk).where(Chunk.id == chunk_id)
        )
        return result.scalar_one_or_none()

    async def delete_by_resource(self, resource_uuid: uuid.UUID) -> int:
        result = await self.session.execute(
            delete(Chunk).where(Chunk.resource_uuid == resource_uuid)
        )
        return result.rowcount