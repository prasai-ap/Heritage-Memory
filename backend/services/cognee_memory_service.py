import logging
import os
from pathlib import Path
from typing import Any

from backend.models.schemas import Memory, MemoryCreate
from backend.services.embedding_service import EmbeddingService
from backend.services.storage_service import LocalStorageService

logger = logging.getLogger(__name__)


class CogneeMemoryService:
    """Persistent memory facade.

    Local JSON is the dependable source of truth for the MVP. When Cognee is
    installed, every remember/improve operation is also indexed into Cognee for
    semantic recall. Any integration failure degrades quietly to local search.
    """

    def __init__(self) -> None:
        storage_path = os.getenv("COGNEE_STORAGE_PATH", "./data/cognee")
        self.storage = LocalStorageService(storage_path)
        self.embeddings = EmbeddingService()
        self._cognee: Any | None = None
        self.mode = "local"
        try:
            import cognee  # type: ignore

            # Cognee otherwise resolves its relative default against the installed
            # package, which may be read-only on local and container installs.
            cognee_root = str((Path(storage_path) / "cognee-system").resolve())
            cognee.config.system_root_directory(cognee_root)
            cognee.config.data_root_directory(str((Path(storage_path) / "cognee-data").resolve()))
            self._cognee = cognee
            self.mode = "cognee+local"
        except Exception as exc:
            logger.info("Cognee unavailable; using local persistent memory: %s", exc)

    @staticmethod
    def _document(memory: Memory) -> str:
        return (
            f"Memory ID: {memory.memory_id}\nElder: {memory.elder_name}\nPlace: {memory.location}\n"
            f"Category: {memory.category}\nTags: {', '.join(memory.tags)}\n{memory.memory_text}"
        )

    async def _index_with_cognee(self, memory: Memory) -> None:
        if not self._cognee:
            return
        try:
            await self._cognee.add(self._document(memory), dataset_name="heritage_memories")
            await self._cognee.cognify(datasets=["heritage_memories"])
        except Exception as exc:
            logger.warning("Cognee indexing failed; local copy remains available: %s", exc)
            self.mode = "local"
            # Do not repeat an expensive known-failing setup for every demo row.
            self._cognee = None

    async def remember(self, payload: MemoryCreate) -> Memory:
        memory = Memory(**payload.model_dump())
        async with self.storage.lock:
            memories = self.storage.read()
            memories.append(memory)
            self.storage.write(memories)
        await self._index_with_cognee(memory)
        return memory

    async def all(self) -> list[Memory]:
        return self.storage.read()

    async def get(self, memory_id: str) -> Memory | None:
        return next((m for m in self.storage.read() if m.memory_id == memory_id), None)

    async def recall(self, question: str, limit: int = 5) -> list[Memory]:
        memories = self.storage.read()
        documents = [
            " ".join([
                memory.elder_name, memory.location, memory.category,
                memory.memory_text, *memory.tags,
            ]) for memory in memories
        ]
        scores = self.embeddings.rank(question, documents) if documents else []
        ranked = sorted(zip(scores, memories), key=lambda item: item[0], reverse=True)
        # A low threshold avoids presenting unrelated culture as evidence.
        return [memory for score, memory in ranked if score >= 0.08][:limit]

    async def improve(self, memory_id: str, detail: str, correction: bool) -> Memory | None:
        from datetime import datetime, timezone

        async with self.storage.lock:
            memories = self.storage.read()
            target = next((m for m in memories if m.memory_id == memory_id), None)
            if not target:
                return None
            target.revisions.append({
                "text": target.memory_text,
                "changed_at": target.updated_at,
                "kind": "correction" if correction else "addition",
            })
            target.memory_text = detail if correction else f"{target.memory_text}\n\nAdditional detail: {detail}"
            target.updated_at = datetime.now(timezone.utc).isoformat()
            self.storage.write(memories)
        await self._index_with_cognee(target)
        return target

    async def forget(self, memory_id: str) -> bool:
        async with self.storage.lock:
            memories = self.storage.read()
            retained = [m for m in memories if m.memory_id != memory_id]
            if len(retained) == len(memories):
                return False
            self.storage.write(retained)
        # Cognee versions expose different deletion APIs. The local record is
        # deleted immediately; a rebuild can reconcile its semantic index.
        return True
