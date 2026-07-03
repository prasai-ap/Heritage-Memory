from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import AliasChoices, BaseModel, Field


class MemoryCreate(BaseModel):
    elder_name: str = Field(min_length=1, max_length=120)
    location: str = Field(min_length=1, max_length=160)
    category: str = Field(min_length=1, max_length=100)
    memory_text: str = Field(min_length=3)
    tags: list[str] = Field(default_factory=list)


class Memory(MemoryCreate):
    memory_id: str = Field(default_factory=lambda: str(uuid4()), validation_alias=AliasChoices("memory_id", "id"))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    revisions: list[dict[str, Any]] = Field(default_factory=list)


class RecallRequest(BaseModel):
    question: str = Field(min_length=2)
    limit: int = Field(default=5, ge=1, le=20)


class RecallResponse(BaseModel):
    answer: str
    memories: list[Memory]
    llm_mode: str


class ImproveRequest(BaseModel):
    memory_id: str
    additional_detail: str = Field(min_length=2)
    correction: bool = False


class MessageResponse(BaseModel):
    message: str


class GraphNode(BaseModel):
    id: str
    label: str
    type: str


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str = ""


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
