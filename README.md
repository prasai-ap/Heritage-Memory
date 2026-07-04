# Heritage Memory

> **Preserving oral culture with persistent AI memory.**

Heritage Memory is a community archive for the knowledge elders carry: stories, recipes, festivals, farming practices, language, crafts, rituals, and local history. It turns each contribution into persistent, connected memory that can be recalled, improved, and—when consent changes—forgotten.

## Problem and solution

Oral culture often lives in one person, one kitchen, or one village gathering. When it is not carried forward, context, relationships, language, and lived experience disappear with it.

Heritage Memory captures a story with its elder, place, category, and themes. A Cognee-ready memory layer connects that context into a graph; multilingual embeddings retrieve relevant memories; Gemini explains only what the archive supports. Every answer shows its source threads.

This is **not a chatbot**. A chatbot starts with a prompt. Heritage Memory starts with consent and a durable lifecycle:

**Remember → Recall → Improve → Forget**

## Why Cognee

Culture is relational. A festival connects a person, place, food, ritual, and community. Cognee's graph-oriented persistent memory makes those relationships discoverable. The included adapter mirrors data into Cognee when available and degrades to a complete local JSON/vector workflow when it is not. Local storage remains the durable source of truth, so a Cognee or network failure never blocks preservation.

## Features

- Story-centered capture with generated summaries and consent
- Grounded recall with elders, locations, tags, source memories, and relevance
- Interactive elder → place/category → memory → tag graph
- Append-only improvement history and immediate privacy-aware forgetting
- Chronological timeline and cultural intelligence dashboard
- Eight emotionally grounded Nepal demo memories
- Live Gemini, Cognee, embedding, and fallback status panel
- Offline-capable mock mode and persistent local storage

## Architecture

Elder's oral memory → FastAPI lifecycle service → persistent storage + optional Cognee + Hugging Face embeddings → grounded Gemini answer → Streamlit graph and source evidence.

## Tech stack

FastAPI · Streamlit · Cognee-ready adapter · Gemini · Sentence Transformers · vis-network · Pydantic · Docker Compose

## Run locally

1. Copy .env.example to .env.
2. Run: pip install -r requirements.txt
3. Run the API: uvicorn backend.main:app --reload
4. In another terminal run: streamlit run frontend/app.py
5. Open http://localhost:8501. API docs are at http://localhost:8000/docs.

No API key is required: summaries and answers use a deterministic grounded fallback. Add GEMINI_API_KEY to .env for Gemini. The Hugging Face model downloads on first use; lexical similarity remains available if it cannot.

For a Cognee-enabled local environment, install requirements-cognee.txt. Cognee remains optional because its platform dependencies vary; the status panel shows whether the adapter connected.

## Docker

Copy .env.example to .env, then run: docker compose up --build

Named Docker volumes preserve both cultural memories and downloaded model weights across restarts.
The Docker image bakes in the multilingual embedding weights for deterministic offline startup. Compose also persists the model cache and allows a three-minute health-check grace period.

## Winning demo flow

1. Open **Home** and frame cultural loss as a memory problem.
2. Load the eight Nepal stories from **Demo Dataset**.
3. Reveal the connected elders, places, categories, memories, and tags in **Memory Graph**.
4. Ask “How was Dashain celebrated in the village?” and inspect the sources.
5. In **Improve**, add “Jamara was grown at home before Dashain.”
6. Ask “What was prepared before Dashain?” and show that recall has changed.
7. Use **Forget** to remove a memory whose consent has changed.
8. Return to **Memory Graph** and **Insights** to show both updating immediately.

## Reliability and cultural safeguards

- Answers are generated only from retrieved memories; insufficient context is stated plainly.
- Every recalled answer exposes its elders, locations, tags, and source records.
- Mock mode remains fully grounded and works without an API key.
- Cached embeddings work without network access, then fall back to lexical relevance if needed.
- Forgetting removes the local source record immediately. Production deployments should additionally verify deletion in every configured Cognee store.

## Track alignment

Persistent AI memory is the product itself. The project visibly proves remember, recall, improve, forget, graph relationships, semantic retrieval, and durable storage. The fallback ensures the social-impact story survives flaky demo Wi-Fi.

## Social impact and roadmap

Heritage Memory centers attribution, consent, source transparency, cultural respect, and removal. Next: consent-linked audio, speaker-approved edits, native-language transcription, community governance, encryption, granular visibility, archive export, and production-grade Cognee deletion synchronization.

## Screenshots

| Home | Living graph | Grounded recall |
|---|---|---|
| _Add demo screenshot_ | _Add demo screenshot_ | _Add demo screenshot_ |
