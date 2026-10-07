from pathlib import Path
import re
import secrets
import string
import aiofiles
from fastapi import UploadFile
from ..core.config import Settings


class FileService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.files_dir = Path("assets/files")

    async def save_file(
    self,
    file: UploadFile,
    project_id: str,
    ):
        file_path, stored_filename = self.generate_unique_filepath(
            file.filename,
            project_id,
        )

        async with aiofiles.open(file_path, "wb") as buffer:
            while chunk := await file.read(
                self.settings.FILE_DEFAULT_CHUNK_SIZE
            ):
                await buffer.write(chunk)

        return stored_filename


    def validate_file(self, content_type, file_size):
        if content_type not in self.settings.FILE_ALLOWED_TYPES:
            return False, "File type is not supported"
        max_size_bytes = self.settings.FILE_MAX_SIZE * 1024 * 1024
        if file_size > max_size_bytes:
            return False, "File size exceeded"
        return True, "valid file"

    def validate_project_id(self, project_id: str) -> bool:
        return bool(re.fullmatch(r"[a-zA-Z0-9_-]+", project_id))

    def get_project_directory(self, project_id: str) -> Path:
        if not self.validate_project_id(project_id):
            raise ValueError("Invalid project ID")

        project_dir = self.files_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir
    
    def generate_unique_filepath(self, orig_file_name: str, project_id: str):
        random_key = self.generate_random_string()
        project_path = self.get_project_directory(project_id)

        cleaned_file_name = self.get_clean_file_name(
            orig_file_name=orig_file_name
        )
        new_file_path = project_path / f"{random_key}_{cleaned_file_name}"
        while new_file_path.exists():
            random_key = self.generate_random_string()
            new_file_path = project_path / f"{random_key}_{cleaned_file_name}"

        return new_file_path, random_key + "_" + cleaned_file_name

    def get_clean_file_name(self, orig_file_name: str):
        cleaned_file_name = re.sub(r'[^\w. ]','', orig_file_name.strip())
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name

    def generate_random_string(self, length: int = 8) -> str:
        characters = string.ascii_letters + string.digits
        return "".join(secrets.choice(characters) for _ in range(length))



    
    