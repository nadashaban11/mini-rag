import unittest

from mini_rag.core.exceptions import LLMProviderError
from mini_rag.services.embedding_service import EmbeddingService


class FakeLLM:
    def __init__(self, dim: int = 3):
        self.calls: list[list[str]] = []
        self.dim = dim

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(list(texts))
        return [[float(len(text))] * self.dim for text in texts]


class WrongCountLLM:
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 3 for _ in texts[:-1]]


class EmbeddingServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_input_skips_provider(self) -> None:
        llm = FakeLLM()
        service = EmbeddingService(llm, batch_size=2, embedding_size=3)

        self.assertEqual(await service.embed_texts([]), [])
        self.assertEqual(llm.calls, [])

    async def test_batches_preserve_order(self) -> None:
        llm = FakeLLM()
        service = EmbeddingService(llm, batch_size=2, embedding_size=3)

        vectors = await service.embed_texts(
            ["a", "bb", "ccc", "dddd", "eeeee"]
        )

        self.assertEqual(
            llm.calls,
            [["a", "bb"], ["ccc", "dddd"], ["eeeee"]],
        )
        self.assertEqual([vector[0] for vector in vectors], [1.0, 2.0, 3.0, 4.0, 5.0])

    async def test_dimension_mismatch_raises(self) -> None:
        service = EmbeddingService(FakeLLM(dim=4), batch_size=2, embedding_size=3)

        with self.assertRaises(LLMProviderError):
            await service.embed_texts(["x"])

    async def test_count_mismatch_raises(self) -> None:
        service = EmbeddingService(WrongCountLLM(), batch_size=2, embedding_size=3)

        with self.assertRaises(LLMProviderError):
            await service.embed_texts(["x", "y"])
