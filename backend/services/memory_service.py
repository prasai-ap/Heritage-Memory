import logging

from backend.models.schemas import Improvement, Memory, MemoryCreate, utc_now
from backend.services.cognee_memory_service import CogneeMemoryService
from backend.services.embedding_service import EmbeddingService
from backend.services.gemini_service import GeminiService
from backend.services.storage_service import StorageService

logger = logging.getLogger(__name__)


class MemoryService:
    def __init__(self, storage=None, embeddings=None, gemini=None, cognee=None):
        self.storage = storage or StorageService()
        self.embeddings = embeddings or EmbeddingService()
        self.gemini = gemini or GeminiService()
        self.cognee = cognee or CogneeMemoryService()

    async def remember(self, payload: MemoryCreate) -> Memory:
        memory = Memory(**payload.model_dump())
        memory.tags = list(dict.fromkeys(t.strip().casefold() for t in memory.tags if t.strip()))
        memory.summary = self.gemini.summarize(memory.memory_text)
        self.storage.upsert(memory)
        await self.cognee.remember_memory(memory)
        return memory

    async def recall(self, query: str, limit: int = 4) -> tuple[list[Memory], list[float]]:
        memories = self.storage.all()
        docs = [" ".join([m.memory_text, m.summary, m.elder_name, m.location, m.category, *m.tags]) for m in memories]
        scores = self.embeddings.rank(query, docs)
        ranked = sorted(zip(memories, scores), key=lambda item: item[1], reverse=True)
        # Lexical fallback uses zero as reliable evidence of no overlap. Neural
        # embeddings may express relevant multilingual matches at lower scores.
        threshold = 0.01 if self.embeddings.mode == "lexical-fallback" else 0.18
        selected = [(m, s) for m, s in ranked[:limit] if s >= threshold]
        return [m for m, _ in selected], [round(s, 4) for _, s in selected]

    async def improve(self, memory_id: str, detail: str) -> Memory | None:
        memory = self.storage.get(memory_id)
        if not memory:
            return None
        memory.improvements.append(Improvement(text=detail))
        memory.memory_text = memory.memory_text.rstrip().rstrip(".") + ". " + detail.strip()
        memory.summary = self.gemini.summarize(memory.memory_text)
        memory.updated_at = utc_now()
        self.storage.upsert(memory)
        await self.cognee.improve_memory(memory)
        return memory

    async def forget(self, memory_id: str) -> Memory | None:
        memory = self.storage.delete(memory_id)
        if memory:
            await self.cognee.forget_memory(memory_id)
        return memory

