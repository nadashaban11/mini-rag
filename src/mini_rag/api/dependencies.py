from collections.abc import AsyncIterator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from mini_rag.core.config import Settings, get_settings
from mini_rag.repositories import (
    ChunkRepository,
    ProjectRepository,
    ResourceRepository,
)
from mini_rag.services.file_service import FileService
from mini_rag.services.process_service import ProcessService
from mini_rag.services.resource_service import ResourceService


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

def get_file_service(
    settings: Settings = Depends(get_settings),
) -> FileService:
    return FileService(settings)

def get_project_repository(
    session: AsyncSession = Depends(get_session),
) -> ProjectRepository:
    return ProjectRepository(session)

def get_resource_repository(
    session: AsyncSession = Depends(get_session),
) -> ResourceRepository:
    return ResourceRepository(session)

def get_chunk_repository(
    session: AsyncSession = Depends(get_session),
) -> ChunkRepository:
    return ChunkRepository(session)

def get_resource_service(
    file_service: FileService = Depends(get_file_service),
    project_repo: ProjectRepository = Depends(get_project_repository),
    resource_repo: ResourceRepository = Depends(get_resource_repository),
) -> ResourceService:
    return ResourceService(file_service, project_repo, resource_repo)

def get_process_service(
    file_service: FileService = Depends(get_file_service),
    project_repo: ProjectRepository = Depends(get_project_repository),
    resource_repo: ResourceRepository = Depends(get_resource_repository),
    chunk_repo: ChunkRepository = Depends(get_chunk_repository),
) -> ProcessService:
    return ProcessService(file_service, project_repo, resource_repo, chunk_repo)
