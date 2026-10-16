import logging

from openai import AsyncOpenAI

from ...core.exceptions import LLMNotConfiguredError, LLMProviderError
from ..enums import DocumentTypeEnum, OpenAIEnums
from ..interface import LLMInterface

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMInterface):

    def __init__(
        self,
        api_key: str,
        base_url: str | None = None,
        default_generation_max_output_tokens: int = 1000,
        default_generation_temperature: float = 0.1,
    ):
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    async def generate_text(
        self,
        prompt: str,
        chat_history: list[dict] | None = None,
        max_output_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        if not self.generation_model_id:
            raise LLMNotConfiguredError("Generation model for OpenAI was not set")

        max_output_tokens = (
            max_output_tokens
            if max_output_tokens is not None
            else self.default_generation_max_output_tokens
        )
        temperature = (
            temperature
            if temperature is not None
            else self.default_generation_temperature
        )

        messages = [
            *(chat_history or []),
            self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value),
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.generation_model_id,
                messages=messages,
                max_tokens=max_output_tokens,
                temperature=temperature,
            )
        except Exception as exc:
            logger.exception("OpenAI generation failed")
            raise LLMProviderError() from exc

        content = response.choices[0].message.content if response.choices else None
        if not content:
            raise LLMProviderError("OpenAI returned an empty response")
        return content

    async def embed_text(
        self,
        text: str,
        document_type: DocumentTypeEnum | None = None,
    ) -> list[float]:
        if not self.embedding_model_id:
            raise LLMNotConfiguredError("Embedding model for OpenAI was not set")

        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model_id,
                input=text,
            )
        except Exception as exc:
            logger.exception("OpenAI embedding failed")
            raise LLMProviderError() from exc

        if not response.data:
            raise LLMProviderError("OpenAI returned no embedding")
        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role: str) -> dict:
        return {"role": role, "content": prompt.strip()}

    async def aclose(self) -> None:
        await self.client.close()