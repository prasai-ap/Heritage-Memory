from fastapi.testclient import TestClient
from backend.main import app, memory_service
from backend.services.storage_service import StorageService
from backend.services.gemini_service import GeminiService

def test_memory_lifecycle(tmp_path):
    memory_service.storage = StorageService(str(tmp_path / "memories.json"))
    client = TestClient(app)
    created = client.post("/memory/remember", json={"elder_name":"Maya Aama","location":"Kaski","category":"Festival","memory_text":"Families gathered for Dashain and elders gave tika.","tags":["dashain","family"]})
    assert created.status_code == 201
    mid = created.json()["memory_id"]
    assert client.post("/memory/recall", json={"query":"Dashain tika"}).json()["grounded"]
    assert "Jamara" in client.post("/memory/improve", json={"memory_id":mid,"improvement":"Jamara was grown at home."}).json()["memory_text"]
    improved_recall = client.post("/memory/recall", json={"query":"What was prepared before Dashain?"}).json()
    assert "Jamara was grown at home" in improved_recall["answer"]
    assert client.get("/memory/graph").json()["edges"]
    assert client.delete(f"/memory/forget/{mid}").status_code == 200
    assert client.get("/memory/insights").json()["total_memories"] == 0

def test_insufficient_context(tmp_path):
    memory_service.storage = StorageService(str(tmp_path / "empty.json"))
    result = TestClient(app).post("/memory/recall", json={"query":"unknown ceremony"}).json()
    assert not result["grounded"]

def test_demo_dataset_is_idempotent_and_updates_views(tmp_path):
    memory_service.storage = StorageService(str(tmp_path / "demo.json"))
    client = TestClient(app)
    first = client.post("/demo/load-sample-data")
    second = client.post("/demo/load-sample-data")
    assert first.status_code == 200 and first.json()["added"] == 8
    assert second.json()["added"] == 0
    assert client.get("/memory/insights").json()["total_memories"] == 8
    graph = client.get("/memory/graph").json()
    assert any(node["group"] == "elder" for node in graph["nodes"])
    assert any(node["group"] == "tag" for node in graph["nodes"])
    recalled = client.post("/memory/recall", json={"query":"How was Dashain celebrated?"}).json()
    assert recalled["grounded"]
    assert any(m["memory_id"] == "demo-dashain-001" for m in recalled["related_memories"])

def test_gemini_configured_and_failure_fall_back_without_hallucinating(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    service = GeminiService()
    assert service.mode == "grounded-mock"
    assert "enough preserved memory" in service.answer("Anything?", [])

    class Models:
        @staticmethod
        def generate_content(**kwargs):
            return type("Response", (), {"text": "Grounded response"})()
    service.client = type("Client", (), {"models": Models()})()
    assert service._generate("prompt") == "Grounded response"

    class BrokenModels:
        @staticmethod
        def generate_content(**kwargs):
            raise RuntimeError("network unavailable")
    service.client = type("Client", (), {"models": BrokenModels()})()
    assert service._generate("prompt") is None
    assert service.last_error == "network unavailable"

def test_status_exposes_fallbacks():
    payload = TestClient(app).get("/status").json()
    assert payload["storage"] == "persistent-json"
    assert payload["cognee"]["mode"] in {"cognee", "local-fallback"}
    assert payload["embeddings"]["status"] in {"huggingface", "lexical-fallback"}
