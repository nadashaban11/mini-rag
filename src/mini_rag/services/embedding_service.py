from ..core.exceptions import LLMProviderError
from ..llm.interface import LLMInterface


class EmbeddingService:
    def __init__(
        self,
        embedding_llm: LLMInterface,
        batch_size: int,
        embedding_size: int,
    ):
        self.embedding_llm = embedding_llm
        self.batch_size = batch_size
        self.embedding_size = embedding_size

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            batch_texts = texts[start : start + self.batch_size]
            vectors = await self.embedding_llm.embed_texts(batch_texts)

            if len(vectors) != len(batch_texts):
                raise LLMProviderError(
                    f"Embedding provider returned {len(vectors)} vectors "
                    f"for {len(batch_texts)} texts"
                )

            for vector in vectors:
                if len(vector) != self.embedding_size:
                    raise LLMProviderError(
                        f"Embedding provider returned a vector of size "
                        f"{len(vector)}, expected {self.embedding_size}"
                    )

            embeddings.extend(vectors)

        return embeddings
