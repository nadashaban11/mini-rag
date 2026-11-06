import logging
from pathlib import Path
import re
import secrets
import shutil
import string
import aiofiles
from fastapi import UploadFile
from ..core.config import Settings
from ..core.exceptions import (
    FileTooLargeError,
    InvalidFileNameError,
    InvalidFileTypeError,
    InvalidProjectIdError,
)

logger = logging.getLogger(__name__)


class FileService:
    MAX_STORED_FILENAME_BYTES = 246

    def __init__(self, settings: Settings):
        self.settings = settings
        self.files_dir = Path("assets/files")

    @property
    def max_size_bytes(self) -> int:
        return self.settings.FILE_MAX_SIZE * 1024 * 1024

    async def save_file(
        self,
        file: UploadFile,
        project_id: str,
        original_filename: str,
    ) -> tuple[str, int]:
        file_path, stored_filename = self.generate_unique_filepath(
            original_filename,
            project_id,
        )
        max_size_bytes = self.max_size_bytes
        size = 0
        saved = False
        try:
            async with aiofiles.open(file_path, "wb") as buffer:
                while chunk := await file.read(
                    self.settings.FILE_DEFAULT_CHUNK_SIZE
                ):
                    if size + len(chunk) > max_size_bytes:
                        raise FileTooLargeError()
                    size += len(chunk)
                    await buffer.write(chunk)
            saved = True
        finally:
            if not saved:
                try:
                    file_path.unlink(missing_ok=True)
                except OSError as exc:
                    logger.warning(
                        "Failed to remove partial upload %s: %s", file_path, exc
                    )
        return stored_filename, size

    def validate_file(
        self, content_type: str | None, file_size: int | None
    ) -> None:
        if content_type not in self.settings.FILE_ALLOWED_TYPES:
            raise InvalidFileTypeError()
        if file_size is not None and file_size > self.max_size_bytes:
            raise FileTooLargeError()

    def validate_project_id(self, project_id: str) -> bool:
        return bool(re.fullmatch(r"[a-zA-Z0-9_-]+", project_id))

    def validate_filename(self, orig_file_name: str | None) -> str:
        if not orig_file_name:
            raise InvalidFileNameError()

        file_name = Path(orig_file_name.strip()).name
        if not file_name or file_name in {".", ".."}:
            raise InvalidFileNameError()
        return file_name

    def get_project_directory(self, project_id: str) -> Path:
        if not self.validate_project_id(project_id):
            raise InvalidProjectIdError()

        project_dir = self.files_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir
    
    def generate_unique_filepath(
        self, orig_file_name: str, project_id: str
    ) -> tuple[Path, str]:
        random_key = self.generate_random_string()
        project_path = self.get_project_directory(project_id)

        cleaned_file_name = self.get_clean_file_name(orig_file_name=orig_file_name)
        new_file_path = project_path / f"{random_key}_{cleaned_file_name}"
        while new_file_path.exists():
            random_key = self.generate_random_string()
            new_file_path = project_path / f"{random_key}_{cleaned_file_name}"

        return new_file_path, new_file_path.name

    def get_clean_file_name(self, orig_file_name: str) -> str:
        cleaned_file_name = re.sub(r"[^\w. ]", "", orig_file_name.strip())
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        if not cleaned_file_name or set(cleaned_file_name) == {"."}:
            raise InvalidFileNameError()
        if len(cleaned_file_name.encode("utf-8")) > self.MAX_STORED_FILENAME_BYTES:
            raise InvalidFileNameError("File name is too long")

        return cleaned_file_name

    def generate_random_string(self, length: int = 8) -> str:
        characters = string.ascii_letters + string.digits
        return "".join(secrets.choice(characters) for _ in range(length))

    def delete_file(self, project_id: str, stored_filename: str) -> None:
        if not self.validate_project_id(project_id):
            raise InvalidProjectIdError()
        path = self.files_dir / project_id / Path(stored_filename).name
        path.unlink(missing_ok=True)

    def delete_project_directory(self, project_id: str) -> None:
        if not self.validate_project_id(project_id):
            raise InvalidProjectIdError()
        shutil.rmtree(self.files_dir / project_id, ignore_errors=True)

    
    