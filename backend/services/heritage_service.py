import json
from pathlib import Path

from backend.models.schemas import Memory, MemoryCreate, RecallResponse
from backend.services.cognee_memory_service import CogneeMemoryService
from backend.services.gemini_service import GeminiService
from backend.services.graph_service import GraphService


class HeritageService:
    def __init__(self) -> None:
        self.memory = CogneeMemoryService()
        self.gemini = GeminiService()
        self.graph = GraphService()

    async def recall(self, question: str, limit: int) -> RecallResponse:
        memories = await self.memory.recall(question, limit)
        answer = await self.gemini.answer(question, memories)
        return RecallResponse(answer=answer, memories=memories, llm_mode=self.gemini.mode)

    async def load_samples(self, path: Path) -> list[Memory]:
        records = json.loads(path.read_text(encoding="utf-8"))
        existing = await self.memory.all()
        signatures = {(m.elder_name, m.memory_text) for m in existing}
        loaded = []
        for record in records:
            if (record["elder_name"], record["memory_text"]) not in signatures:
                loaded.append(await self.memory.remember(MemoryCreate.model_validate(record)))
        return loaded
