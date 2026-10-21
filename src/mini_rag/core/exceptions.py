class MiniRagError(Exception):
    """Base class for all mini-rag domain errors.

    The single handler in main.py catches this class only,
    so random ValueError/RuntimeError bugs still surface as 500.
    """

    status_code: int = 500
    message: str = "Internal server error"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.message)
        if message is not None:
            self.message = message


class InvalidProjectIdError(MiniRagError):
    """Raised when project_id fails validation."""

    status_code: int = 400
    message: str = "Invalid project ID"


class InvalidFileTypeError(MiniRagError):
    """Raised when uploaded file content type is not allowed."""

    status_code: int = 415
    message: str = "File type is not supported"


class FileTooLargeError(MiniRagError):
    """Raised when uploaded file exceeds the max size."""

    status_code: int = 413
    message: str = "File size exceeded"

class ProjectFileNotFoundError(MiniRagError):
    """Raised when the requested file does not exist in the project folder."""

    status_code: int = 404
    message: str = "File not found"


class UnsupportedProcessingTypeError(MiniRagError):
    """Raised when the file extension has no loader for processing."""

    status_code: int = 415
    message: str = "File type cannot be processed"


class EmptyProcessingResultError(MiniRagError):
    """Raised when processing finishes but produces no chunks."""

    status_code: int = 422
    message: str = "No content could be extracted from the file"

class ProjectNotFoundError(MiniRagError):
    """Raised when the requested project does not exist."""

    status_code: int = 404
    message: str = "Project not found"

class LLMNotConfiguredError(MiniRagError):
    """Raised when an LLM provider is selected but its settings are missing."""

    status_code: int = 500
    message: str = "LLM provider is not configured"


class UnsupportedLLMProviderError(MiniRagError):
    """Raised when the selected LLM provider has no implementation."""

    status_code: int = 500
    message: str = "LLM provider is not supported"


class LLMProviderError(MiniRagError):
    """Raised when a call to the LLM provider fails."""

    status_code: int = 502
    message: str = "The LLM provider request failed"