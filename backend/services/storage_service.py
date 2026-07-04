import json
import os
import threading
from pathlib import Path

from backend.models.schemas import Memory


class StorageService:
    """Small, durable JSON store with atomic replacement and process-local locking."""

    def __init__(self, path: str | None = None):
        self.path = Path(path or os.getenv("MEMORY_STORE_PATH", "data/memories.json"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        if not self.path.exists():
            self._write([])

    def _read(self) -> list[dict]:
        with self._lock:
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, FileNotFoundError):
                return []

    def _write(self, records: list[dict]) -> None:
        with self._lock:
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self.path)

    def all(self) -> list[Memory]:
        return [Memory.model_validate(item) for item in self._read()]

    def get(self, memory_id: str) -> Memory | None:
        return next((m for m in self.all() if m.memory_id == memory_id), None)

    def upsert(self, memory: Memory) -> Memory:
        records = self._read()
        payload = memory.model_dump()
        for index, record in enumerate(records):
            if record.get("memory_id") == memory.memory_id:
                records[index] = payload
                break
        else:
            records.append(payload)
        self._write(records)
        return memory

    def delete(self, memory_id: str) -> Memory | None:
        records = self._read()
        found = next((r for r in records if r.get("memory_id") == memory_id), None)
        if found:
            self._write([r for r in records if r.get("memory_id") != memory_id])
            return Memory.model_validate(found)
        return None

    def insert_many(self, memories: list[Memory]) -> int:
        existing = {m.memory_id: m for m in self.all()}
        before = len(existing)
        existing.update({m.memory_id: m for m in memories})
        self._write([m.model_dump() for m in existing.values()])
        return len(existing) - before

