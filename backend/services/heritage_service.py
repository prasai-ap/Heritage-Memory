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
        # Improvements change text, so stable provenance keeps demo loads idempotent.
        signatures = {(m.elder_name, m.location, m.category) for m in existing}
        loaded = []
        for record in records:
            signature = (record["elder_name"], record["location"], record["category"])
            if signature not in signatures:
                loaded.append(await self.memory.remember(MemoryCreate.model_validate(record)))
                signatures.add(signature)
        return loaded

    @staticmethod
    def sample_records(path: Path) -> list[dict]:
        return json.loads(path.read_text(encoding="utf-8"))
