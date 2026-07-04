import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models.schemas import ImproveRequest, Memory, MemoryCreate, RecallRequest
from backend.services.graph_service import GraphService, InsightService
from backend.services.memory_service import MemoryService

load_dotenv()
logging.basicConfig(level=logging.INFO)
memory_service = MemoryService()
graph_service, insight_service = GraphService(), InsightService()
SAMPLE_DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_memories.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path("data").mkdir(exist_ok=True)
    yield


app = FastAPI(title=os.getenv("APP_NAME", "Heritage Memory"), version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "healthy", "app": "Heritage Memory"}


@app.get("/status")
def status():
    cognee = memory_service.cognee.status()
    return {
        "gemini": {
            "status": memory_service.gemini.mode,
            "model": memory_service.gemini.model_name,
            "last_error": memory_service.gemini.last_error,
        },
        "cognee": cognee,
        "embeddings": {"status": memory_service.embeddings.mode, "model": memory_service.embeddings.model_name},
        "fallback_mode": not cognee["operational"],
        "storage": "persistent-json",
    }


@app.post("/memory/remember", response_model=Memory, status_code=201)
async def remember(payload: MemoryCreate):
    return await memory_service.remember(payload)


@app.post("/memory/recall")
async def recall(payload: RecallRequest):
    memories, scores = await memory_service.recall(payload.query, payload.limit)
    answer = memory_service.gemini.answer(payload.query, memories)
    return {
        "answer": answer, "related_memories": memories, "scores": scores,
        "connected_elders": sorted({m.elder_name for m in memories}),
        "connected_locations": sorted({m.location for m in memories}),
        "connected_tags": sorted({t for m in memories for t in m.tags}),
        "grounded": bool(memories),
    }


@app.post("/memory/improve", response_model=Memory)
async def improve(payload: ImproveRequest):
    result = await memory_service.improve(payload.memory_id, payload.improvement)
    if not result:
        raise HTTPException(404, "Memory not found")
    return result


@app.delete("/memory/forget/{memory_id}")
async def forget(memory_id: str):
    result = await memory_service.forget(memory_id)
    if not result:
        raise HTTPException(404, "Memory not found")
    return {"message": "Memory removed with care.", "forgotten_memory": result}


@app.get("/memory/all", response_model=list[Memory])
def all_memories():
    return memory_service.storage.all()


@app.get("/memory/graph")
def graph():
    return graph_service.build(memory_service.storage.all())


@app.get("/memory/insights")
def insights():
    return insight_service.calculate(memory_service.storage.all())


@app.get("/demo/sample-memories")
def samples():
    return json.loads(SAMPLE_DATA_PATH.read_text(encoding="utf-8"))


@app.post("/demo/load-sample-data")
def load_samples():
    items = [Memory.model_validate(item) for item in samples()]
    added = memory_service.storage.insert_many(items)
    return {"message": f"{added} new cultural memories preserved.", "added": added, "total": len(memory_service.storage.all())}
