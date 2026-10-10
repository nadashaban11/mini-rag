from pathlib import Path
from typing import NamedTuple

from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..core.exceptions import (
    EmptyProcessingResultError,
    ProjectFileNotFoundError,
    UnsupportedProcessingTypeError,
)
from .file_service import FileService


class LoaderSpec(NamedTuple):
    loader_cls: type
    kwargs: dict


LOADERS: dict[str, LoaderSpec] = {
    ".txt": LoaderSpec(TextLoader, {"encoding": "utf-8"}),
    ".pdf": LoaderSpec(PyMuPDFLoader, {}),
}


class ProcessService:
    def __init__(self, file_service: FileService):
        self.file_service = file_service

    def get_file_path(self, project_id: str, file_id: str) -> Path:
        project_dir = self.file_service.get_project_directory(project_id)
        file_path = project_dir / Path(file_id).name
        if not file_path.is_file():
            raise ProjectFileNotFoundError()
        return file_path

    def get_loader(self, file_path: Path):
        spec = LOADERS.get(file_path.suffix.lower())
        if spec is None:
            raise UnsupportedProcessingTypeError()
        return spec.loader_cls(str(file_path), **spec.kwargs)

    def process_file(
        self,
        project_id: str,
        file_id: str,
        chunk_size: int,
        overlap_size: int,
    ):
        file_path = self.get_file_path(project_id, file_id)
        documents = self.get_loader(file_path).load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )
        chunks = splitter.split_documents(documents)

        if not chunks:
            raise EmptyProcessingResultError()
        return chunks