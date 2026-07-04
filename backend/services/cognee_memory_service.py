import importlib.util
import logging
import os

from backend.models.schemas import Memory

logger = logging.getLogger(__name__)


class CogneeMemoryService:
    """Optional Cognee adapter. Local storage remains the durable source of truth.

    Cognee APIs have evolved rapidly; this adapter detects the package and mirrors
    memories when its public add/cognify/search functions are available. Any error
    degrades safely to the fully functional local memory layer.
    """

    def __init__(self):
        self.enabled = os.getenv("USE_COGNEE", "true").lower() == "true"
        self.available = bool(importlib.util.find_spec("cognee")) if self.enabled else False
        self.last_error = None

    async def remember_memory(self, memory: Memory) -> bool:
        if not self.available:
            logger.info("Using fallback memory")
            return False
        try:
            import cognee
            await cognee.add(memory.model_dump_json(), dataset_name="heritage_memory")
            await cognee.cognify()
            logger.info("Using Cognee memory")
            return True
        except Exception as exc:
            self.last_error = str(exc)
            logger.warning("Using fallback memory: %s", exc)
            return False

    async def recall_memory(self, query: str):
        if not self.available:
            return None
        try:
            import cognee
            return await cognee.search(query_text=query)
        except Exception as exc:
            self.last_error = str(exc)
            return None

    async def improve_memory(self, memory: Memory) -> bool:
        return await self.remember_memory(memory)

    async def forget_memory(self, memory_id: str) -> bool:
        # Deletion APIs differ by Cognee release. The local source of truth is
        # deleted immediately; a supported adapter can be added without API changes.
        logger.info("Forget requested for Cognee memory %s", memory_id)
        return self.available

    def status(self) -> dict:
        return {"available": self.available, "enabled": self.enabled, "last_error": self.last_error}

