from ..core.config import Settings
from ..core.exceptions import LLMNotConfiguredError, UnsupportedLLMProviderError
from .enums import LLMEnums
from .interface import LLMInterface
from .providers.openai_provider import OpenAIProvider


class LLMProviderFactory:
    def __init__(self, settings: Settings):
        self.settings = settings

    def create(self, provider: LLMEnums) -> LLMInterface:
        match provider:
            case LLMEnums.OPENAI:
                key = self.settings.OPENAI_API_KEY
                if key is None or not key.get_secret_value():
                    raise LLMNotConfiguredError("OPENAI_API_KEY is not set")
                return OpenAIProvider(
                    api_key=key.get_secret_value(),
                    base_url=self.settings.OPENAI_BASE_URL,
                    default_generation_max_output_tokens=self.settings.GENERATION_DEFAULT_MAX_TOKENS,
                    default_generation_temperature=self.settings.GENERATION_DEFAULT_TEMPERATURE,
                )
        raise UnsupportedLLMProviderError(f"No implementation for {provider}")