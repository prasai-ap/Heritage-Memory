import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

from backend.models.schemas import (  # noqa: E402
    GraphResponse, ImproveRequest, Memory, MemoryCreate, MessageResponse,
    RecallRequest, RecallResponse,
)
from backend.services.heritage_service import HeritageService  # noqa: E402

app = FastAPI(title=os.getenv("APP_NAME", "Heritage Memory"), version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)
service = HeritageService()
SAMPLE_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_memories.json"


@app.get("/health")
async def health() -> dict:
    return {"status": "healthy", "app": app.title, "memory_mode": service.memory.mode, "llm_mode": service.gemini.mode, "embedding_mode": service.memory.embeddings.mode}


@app.post("/memory/remember", response_model=Memory, status_code=201)
async def remember(payload: MemoryCreate) -> Memory:
    return await service.memory.remember(payload)


@app.get("/memory", response_model=list[Memory])
async def list_memories() -> list[Memory]:
    """Return the archive for timeline and stewardship views."""
    return await service.memory.all()


@app.post("/memory/recall", response_model=RecallResponse)
async def recall(payload: RecallRequest) -> RecallResponse:
    return await service.recall(payload.question, payload.limit)


@app.post("/memory/improve", response_model=Memory)
async def improve(payload: ImproveRequest) -> Memory:
    memory = await service.memory.improve(payload.memory_id, payload.additional_detail, payload.correction)
    if not memory:
        raise HTTPException(404, "Memory not found")
    return memory


@app.delete("/memory/forget/{memory_id}", response_model=MessageResponse)
async def forget(memory_id: str) -> MessageResponse:
    if not await service.memory.forget(memory_id):
        raise HTTPException(404, "Memory not found")
    return MessageResponse(message="Memory forgotten")


@app.get("/memory/graph", response_model=GraphResponse)
async def graph() -> GraphResponse:
    return service.graph.build(await service.memory.all())


@app.post("/demo/load-sample-data")
async def load_sample_data() -> dict:
    loaded = await service.load_samples(SAMPLE_DATA_PATH)
    return {"message": "Sample heritage loaded", "loaded": len(loaded), "total": len(await service.memory.all())}


@app.post("/demo/reset-sample-data")
async def reset_sample_data() -> dict:
    loaded = await service.reset_samples(SAMPLE_DATA_PATH)
    return {
        "message": "Nepal demo archive reset",
        "loaded": len(loaded),
        "total": len(await service.memory.all()),
    }


@app.get("/demo/sample-memories")
async def sample_memories() -> list[dict]:
    return service.sample_records(SAMPLE_DATA_PATH)
