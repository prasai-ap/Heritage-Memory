import logging
import math
import os
import re

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Lazy multilingual embeddings with a zero-download lexical fallback."""

    def __init__(self) -> None:
        self.model_name = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self._model = None
        self._load_attempted = False
        self.mode = "lexical"

    def _load(self) -> None:
        if self._load_attempted:
            return
        self._load_attempted = True
        try:
            from sentence_transformers import SentenceTransformer

            # Loading is lazy so the API can boot offline. If the model is not
            # cached, Sentence Transformers may download it on the first recall.
            self._model = SentenceTransformer(self.model_name)
            self.mode = "huggingface"
            logger.info("Using Hugging Face embeddings: %s", self.model_name)
        except Exception as exc:
            logger.warning("Embedding model unavailable; using lexical similarity: %s", exc)

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return set(re.findall(r"[\wऀ-ॿ]+", text.lower()))

    def rank(self, question: str, documents: list[str]) -> list[float]:
        self._load()
        if self._model:
            vectors = self._model.encode([question, *documents], normalize_embeddings=True)
            query = vectors[0]
            return [float(sum(a * b for a, b in zip(query, vector))) for vector in vectors[1:]]
        query_tokens = self._tokens(question)
        scores = []
        for document in documents:
            tokens = self._tokens(document)
            denominator = math.sqrt(len(query_tokens) * len(tokens)) or 1
            scores.append(len(query_tokens & tokens) / denominator)
        return scores
