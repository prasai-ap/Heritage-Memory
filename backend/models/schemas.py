from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

CATEGORIES = [
    "Festival", "Recipe", "Farming Practice", "Local History", "Language Phrase",
    "Craft", "Story", "Ritual", "Education Tradition",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Improvement(BaseModel):
    text: str
    created_at: str = Field(default_factory=utc_now)


class MemoryCreate(BaseModel):
    elder_name: str = Field(min_length=2, max_length=120)
    location: str = Field(min_length=2, max_length=160)
    category: str
    memory_text: str = Field(min_length=10, max_length=10000)
    tags: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("category")
    @classmethod
    def supported_category(cls, value: str) -> str:
        if value not in CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(CATEGORIES)}")
        return value


class Memory(MemoryCreate):
    memory_id: str = Field(default_factory=lambda: str(uuid4()))
    summary: str = ""
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)
    improvements: list[Improvement] = Field(default_factory=list)


class RecallRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1000)
    limit: int = Field(default=4, ge=1, le=10)


class ImproveRequest(BaseModel):
    memory_id: str
    improvement: str = Field(min_length=3, max_length=5000)
