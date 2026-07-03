# Heritage Memory

Heritage Memory is a hackathon MVP for preserving oral cultural knowledge. Elders' stories become durable memories that future generations can recall, refine, connect, and—when consent changes—forget. The demo includes seven Nepal heritage memories and runs without cloud credentials.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn backend.main:app --reload
```

In another terminal:

```bash
streamlit run frontend/app.py
```

Open `http://localhost:8501`. API documentation is at `http://localhost:8000/docs`. Alternatively, create `.env` and run `docker compose up --build`.

## Cognee memory lifecycle

The `CogneeMemoryService` keeps the application-facing lifecycle stable while isolating memory infrastructure:

1. **Remember** — `POST /memory/remember` validates an oral account, writes a durable local record, and asks Cognee to add and cognify its semantic document.
2. **Recall** — `POST /memory/recall` retrieves relevant memories. The fallback uses deterministic lexical ranking; Gemini turns retrieved evidence into a grounded answer and cites the elder in prose.
3. **Improve** — `POST /memory/improve` stores the previous text in revision history, applies an addition or correction, then re-indexes the current account. Knowledge can grow without erasing its provenance.
4. **Forget** — `DELETE /memory/forget/{memory_id}` removes the canonical record. The adapter boundary is the place to connect the deletion API for the deployed Cognee version or rebuild its dataset, since Cognee deletion interfaces vary between releases.

Local JSON under `COGNEE_STORAGE_PATH` is intentionally the MVP source of truth. If Cognee cannot import or index, the lifecycle still works. If `GEMINI_API_KEY` is empty or Gemini fails, recall produces a simple grounded answer from the best matching memory. `/health` exposes the active modes.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Readiness and active provider modes |
| POST | `/memory/remember` | Preserve a memory |
| POST | `/memory/recall` | Ask a cultural question |
| POST | `/memory/improve` | Add detail or correct a memory |
| DELETE | `/memory/forget/{memory_id}` | Remove a memory |
| GET | `/memory/graph` | Person → place → category → memory → tags graph |
| POST | `/demo/load-sample-data` | Idempotently load Nepal demo data |

## Notes for a real community deployment

Capture informed consent, access rules, language and clan restrictions, attribution preferences, and deletion policy before collection. Encrypt sensitive records, use authenticated endpoints, and let community stewards govern what an AI may summarize. Oral heritage is relational knowledge, not merely content.
