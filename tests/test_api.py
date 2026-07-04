from fastapi.testclient import TestClient
from backend.main import app, memory_service
from backend.services.storage_service import StorageService

def test_memory_lifecycle(tmp_path):
    memory_service.storage = StorageService(str(tmp_path / "memories.json"))
    client = TestClient(app)
    created = client.post("/memory/remember", json={"elder_name":"Maya Aama","location":"Kaski","category":"Festival","memory_text":"Families gathered for Dashain and elders gave tika.","tags":["dashain","family"]})
    assert created.status_code == 201
    mid = created.json()["memory_id"]
    assert client.post("/memory/recall", json={"query":"Dashain tika"}).json()["grounded"]
    assert "Jamara" in client.post("/memory/improve", json={"memory_id":mid,"improvement":"Jamara was grown at home."}).json()["memory_text"]
    assert client.get("/memory/graph").json()["edges"]
    assert client.delete(f"/memory/forget/{mid}").status_code == 200
    assert client.get("/memory/insights").json()["total_memories"] == 0

def test_insufficient_context(tmp_path):
    memory_service.storage = StorageService(str(tmp_path / "empty.json"))
    result = TestClient(app).post("/memory/recall", json={"query":"unknown ceremony"}).json()
    assert not result["grounded"]
