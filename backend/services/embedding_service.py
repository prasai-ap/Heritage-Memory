import logging
import math
import os
import re
from collections import Counter

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.model_name = os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.model = None
        self.mode = "lexical-fallback"
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.mode = "huggingface"
        except Exception as exc:
            logger.warning("Embedding model unavailable; using lexical similarity: %s", exc)

    @staticmethod
    def _tokens(text: str) -> Counter:
        return Counter(re.findall(r"[^\W_]+", text.casefold(), flags=re.UNICODE))

    def rank(self, query: str, documents: list[str]) -> list[float]:
        if not documents:
            return []
        if self.model:
            vectors = self.model.encode([query, *documents], normalize_embeddings=True)
            return [float(vectors[0] @ vector) for vector in vectors[1:]]
        query_tokens = self._tokens(query)
        scores = []
        for document in documents:
            doc_tokens = self._tokens(document)
            overlap = sum((query_tokens & doc_tokens).values())
            denom = math.sqrt(sum(query_tokens.values()) * sum(doc_tokens.values())) or 1
            scores.append(overlap / denom)
        return scores

