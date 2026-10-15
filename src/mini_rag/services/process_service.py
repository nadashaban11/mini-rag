import asyncio
from pathlib import Path
from typing import NamedTuple

from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..core.exceptions import (
    EmptyProcessingResultError,
    ProjectFileNotFoundError,
    UnsupportedProcessingTypeError,
)
from ..models import Chunk
from ..repositories import ChunkRepository
from .file_service import FileService
from .resource_service import ResourceService


class LoaderSpec(NamedTuple):
    loader_cls: type
    kwargs: dict


LOADERS: dict[str, LoaderSpec] = {
    ".txt": LoaderSpec(TextLoader, {"encoding": "utf-8"}),
    ".pdf": LoaderSpec(PyMuPDFLoader, {}),
}


class ProcessService:
    def __init__(
        self,
        file_service: FileService,
        resource_service: ResourceService,
        chunk_repo: ChunkRepository,
    ):
        self.file_service = file_service
        self.resource_service = resource_service
        self.chunk_repo = chunk_repo

    def get_file_path(self, project_id: str, stored_filename: str) -> Path:
        project_dir = self.file_service.get_project_directory(project_id)
        file_path = project_dir / stored_filename
        if not file_path.is_file():
            raise ProjectFileNotFoundError()
        return file_path

    def get_loader(self, file_path: Path):
        spec = LOADERS.get(file_path.suffix.lower())
        if spec is None:
            raise UnsupportedProcessingTypeError()
        return spec.loader_cls(str(file_path), **spec.kwargs)

    def load_and_split(self, file_path: Path, chunk_size: int, overlap_size: int):
        documents = self.get_loader(file_path).load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )
        return splitter.split_documents(documents)

    async def process_file(
        self,
        project_id: str,
        file_id: str,
        chunk_size: int,
        overlap_size: int,
    ) -> int:
        resource = await self.resource_service.get(project_id, file_id)
        file_path = self.get_file_path(project_id, resource.stored_filename)

        docs = await asyncio.to_thread(
            self.load_and_split, file_path, chunk_size, overlap_size
        )
        if not docs:
            raise EmptyProcessingResultError()

        await self.chunk_repo.delete_by_resource(resource.id)
        chunks = [
            Chunk(
                resource_uuid=resource.id,
                chunk_order=i,
                chunk_text=doc.page_content,
                chunk_metadata={
                    k: v for k, v in doc.metadata.items() if k == "page"
                },
            )
            for i, doc in enumerate(docs)
        ]
        return await self.chunk_repo.add_many(chunks)