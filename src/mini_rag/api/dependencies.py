from fastapi import Depends

from mini_rag.core.config import Settings, get_settings
from mini_rag.services.file_service import FileService


def get_file_service(
    settings: Settings = Depends(get_settings),
) -> FileService:
    return FileService(settings)