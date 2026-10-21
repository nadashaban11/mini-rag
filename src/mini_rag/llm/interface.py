from abc import ABC, abstractmethod

from .enums import DocumentTypeEnum


class LLMInterface(ABC):

    @abstractmethod
    def set_generation_model(self, model_id: str):
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        chat_history: list[dict] | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        pass

    @abstractmethod
    async def embed_text(
        self,
        text: str,
        document_type: DocumentTypeEnum | None = None,
    ) -> list[float]:
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str) -> dict:
        pass

    async def aclose(self) -> None:
        return None