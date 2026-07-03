import asyncio
import json
import logging
from pathlib import Path

from backend.models.schemas import Memory

logger = logging.getLogger(__name__)


class LocalStorageService:
    """Small, atomic JSON store used as the reliable local persistence layer."""

    def __init__(self, storage_path: str) -> None:
        directory = Path(storage_path)
        directory.mkdir(parents=True, exist_ok=True)
        self.file = directory / "memories.json"
        self.lock = asyncio.Lock()

    def read(self) -> list[Memory]:
        if not self.file.exists():
            return []
        try:
            return [Memory.model_validate(item) for item in json.loads(self.file.read_text(encoding="utf-8"))]
        except Exception as exc:
            logger.error("Unable to read fallback memory store: %s", exc)
            return []

    def write(self, memories: list[Memory]) -> None:
        temporary = self.file.with_suffix(".tmp")
        temporary.write_text(
            json.dumps([memory.model_dump() for memory in memories], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.file)
