from fastapi import Depends

from mini_rag.core.config import Settings, get_settings
from mini_rag.services.file_service import FileService
from mini_rag.services.process_service import ProcessService

def get_file_service(
    settings: Settings = Depends(get_settings),
) -> FileService:
    return FileService(settings)

def get_process_service(
    file_service: FileService = Depends(get_file_service),
) -> ProcessService:
    return ProcessService(file_service)