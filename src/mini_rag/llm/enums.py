from enum import StrEnum


class LLMEnums(StrEnum):
    OPENAI = "openai"
    COHERE = "cohere"


class OpenAIEnums(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class DocumentTypeEnum(StrEnum):
    DOCUMENT = "document"
    QUERY = "query"