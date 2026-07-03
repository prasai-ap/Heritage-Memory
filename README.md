# Heritage Memory

> **Preserving oral culture with persistent AI memory.**

Heritage Memory is an AI-powered cultural archive for stories, traditions, recipes, festivals, local history, farming practices, language phrases, crafts, and teaching traditions shared by elders and communities.

## The problem

Oral knowledge often disappears when elders pass away, families migrate, or local languages lose speakers. Conventional archives are difficult to contribute to, while ordinary chatbots forget conversations and cannot show how knowledge evolved or honor a request to remove it.

## The solution

Heritage Memory turns each contributed account into attributable, persistent memory. People can retrieve knowledge through natural questions, refine an account when an elder adds context, see relationships between people and traditions, and remove knowledge when consent changes. Gemini answers only from retrieved memory; multilingual Hugging Face embeddings make local recall useful across diverse expressions.

## Why persistent memory—and why Cognee?

Cognee's memory model fits cultural knowledge better than a one-off prompt. A remembered account can be retrieved in a later session and connected to elders, places, categories, and tags. The service boundary keeps Cognee indexing clear while an atomic JSON store makes the hackathon demo dependable offline.

This is **not a normal chatbot**: the conversation is only a doorway. The product's core is a governed archive with provenance, revisions, deletion, semantic retrieval, and a visible cultural graph.

## Features

- Remember structured oral accounts with elder, place, category, text, and tags
- Recall grounded answers with Gemini and show every supporting memory
- Improve memories while retaining revision history
- Forget memories to support privacy and continuing consent
- Explore `Elder → Location → Category → Memory → Tags` visually
- Search locally with multilingual Sentence Transformers embeddings
- Run without Gemini, Cognee, or an internet connection using graceful fallbacks
- Load eight Nepal-focused stories in one click

## Architecture

```text
                         ┌──────────── Gemini grounded answer
Streamlit ──► FastAPI ──► Heritage service
                         ├──────────── Cognee semantic memory
                         ├──────────── JSON persistent fallback
                         ├──────────── Hugging Face embeddings
                         └──────────── PyVis relationship graph
```

## Memory lifecycle

| Action | Cultural purpose | Implementation |
|---|---|---|
| Remember | Store an oral memory with provenance | Persist locally, then add and cognify in Cognee |
| Recall | Answer from remembered cultural context | Rank with multilingual embeddings; Gemini uses only retrieved evidence |
| Improve | Add corrections or details | Preserve the previous text as a revision and re-index the current account |
| Forget | Remove private, withdrawn, or outdated knowledge | Delete the canonical record and remove it from the visible graph |

## Tech stack

FastAPI, Streamlit, Cognee, Gemini (`google-genai`), Sentence Transformers, PyVis/NetworkX, Pydantic, JSON storage, and Docker Compose.

## Run locally

Python 3.11 is recommended.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn backend.main:app --reload
```

In a second terminal:

```powershell
.venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```

Open `http://localhost:8501`; interactive API docs are at `http://localhost:8000/docs`. Add `GEMINI_API_KEY` to `.env` for generated answers. With no key, grounded mock responses keep the demo working.

### Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

The frontend connects to the backend service internally and is exposed on port 8501.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Provider modes and readiness |
| POST | `/memory/remember` | Preserve an oral account |
| POST | `/memory/recall` | Recall grounded knowledge |
| POST | `/memory/improve` | Correct or expand a memory |
| DELETE | `/memory/forget/{memory_id}` | Withdraw a memory |
| GET | `/memory/graph` | Return graph nodes and relationships |
| POST | `/demo/load-sample-data` | Idempotently load the demo archive |
| GET | `/demo/sample-memories` | Preview the sample dataset |

## Three-minute demo script

1. Open **Home** and explain why persistent, governable memory matters.
2. Load the Nepal demo dataset and preview its eight accounts.
3. Recall “What did elders teach children?” and reveal the supporting memories.
4. Open **Memory Graph** to show knowledge connected across people, places, and tags.
5. Add a detail in **Improve**, showing that knowledge evolves without losing history.
6. Explain **Forget** as a privacy and consent feature, then remove a demo record.
7. End on `/health`: the same experience works with cloud providers or local fallbacks.

## Screenshots

> Add final submission captures here: Home · Grounded recall · Cultural graph · Improve lifecycle.

## Track alignment and social impact

Heritage Memory demonstrates persistent AI memory as the product primitive—not a chat feature. It helps communities build searchable intergenerational archives while keeping provenance, correction, and withdrawal visible. Community stewardship is essential: production deployments should include informed consent, role-based access, culturally restricted knowledge, encryption, and local-language governance.

## Roadmap

- Audio recording, transcription, speaker consent, and source playback
- Nepali and community-language interfaces
- Community steward roles and granular knowledge permissions
- Cognee-native deletion reconciliation and graph synchronization
- Contradiction review, citations, confidence indicators, and offline-first mobile capture
- Encrypted backups and community-owned hosting
