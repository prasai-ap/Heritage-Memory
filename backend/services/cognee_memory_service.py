import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from backend.models.schemas import Memory, MemoryCreate

logger = logging.getLogger(__name__)


class CogneeMemoryService:
    """Persistent memory facade.

    Local JSON is the dependable source of truth for the MVP. When Cognee is
    installed, every remember/improve operation is also indexed into Cognee for
    semantic recall. Any integration failure degrades quietly to local search.
    """

    def __init__(self) -> None:
        storage = Path(os.getenv("COGNEE_STORAGE_PATH", "./data/cognee"))
        storage.mkdir(parents=True, exist_ok=True)
        self.file = storage / "memories.json"
        self._lock = asyncio.Lock()
        self._cognee: Any | None = None
        self.mode = "local"
        try:
            import cognee  # type: ignore

            self._cognee = cognee
            self.mode = "cognee+local"
        except Exception as exc:
            logger.info("Cognee unavailable; using local persistence: %s", exc)

    def _read(self) -> list[Memory]:
        if not self.file.exists():
            return []
        try:
            return [Memory.model_validate(item) for item in json.loads(self.file.read_text(encoding="utf-8"))]
        except Exception as exc:
            logger.error("Could not read memory store: %s", exc)
            return []

    def _write(self, memories: list[Memory]) -> None:
        temp = self.file.with_suffix(".tmp")
        temp.write_text(json.dumps([m.model_dump() for m in memories], ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(self.file)

    @staticmethod
    def _document(memory: Memory) -> str:
        return (
            f"Memory ID: {memory.id}\nElder: {memory.elder_name}\nPlace: {memory.location}\n"
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

    async def remember(self, payload: MemoryCreate) -> Memory:
        memory = Memory(**payload.model_dump())
        async with self._lock:
            memories = self._read()
            memories.append(memory)
            self._write(memories)
        await self._index_with_cognee(memory)
        return memory

    async def all(self) -> list[Memory]:
        return self._read()

    async def get(self, memory_id: str) -> Memory | None:
        return next((m for m in self._read() if m.id == memory_id), None)

    async def recall(self, question: str, limit: int = 5) -> list[Memory]:
        # Deterministic lexical ranking remains available even when Cognee is down.
        terms = set(re.findall(r"[\wऀ-ॿ]+", question.lower()))
        memories = self._read()

        def score(memory: Memory) -> tuple[int, str]:
            haystack = " ".join([
                memory.elder_name, memory.location, memory.category,
                memory.memory_text, *memory.tags,
            ]).lower()
            return (sum(1 + (term in memory.category.lower()) for term in terms if term in haystack), memory.updated_at)

        ranked = sorted(memories, key=score, reverse=True)
        matches = [m for m in ranked if score(m)[0] > 0]
        return (matches or ranked)[:limit]

    async def improve(self, memory_id: str, detail: str, correction: bool) -> Memory | None:
        from datetime import datetime, timezone

        async with self._lock:
            memories = self._read()
            target = next((m for m in memories if m.id == memory_id), None)
            if not target:
                return None
            target.revisions.append({
                "text": target.memory_text,
                "changed_at": target.updated_at,
                "kind": "correction" if correction else "addition",
            })
            target.memory_text = detail if correction else f"{target.memory_text}\n\nAdditional detail: {detail}"
            target.updated_at = datetime.now(timezone.utc).isoformat()
            self._write(memories)
        await self._index_with_cognee(target)
        return target

    async def forget(self, memory_id: str) -> bool:
        async with self._lock:
            memories = self._read()
            retained = [m for m in memories if m.id != memory_id]
            if len(retained) == len(memories):
                return False
            self._write(retained)
        # Cognee versions expose different deletion APIs. The local record is
        # deleted immediately; a rebuild can reconcile its semantic index.
        return True
