# Heritage Memory — Hackathon Submission

## Short description

Heritage Memory preserves elders’ oral culture as persistent AI memory communities can recall, improve, connect, and forget—with Gemini, Cognee, multilingual embeddings, and reliable local fallbacks.

## Long description

Stories, recipes, farming practices, local phrases, festivals, and village history often disappear when elders pass away or communities migrate. Heritage Memory gives communities a simple way to preserve that knowledge as persistent, governed AI memory.

Each account is stored with its elder, place, category, and tags. Later, multilingual embeddings retrieve relevant memories and Gemini answers questions using only that evidence. The source memories remain visible, so users can inspect where an answer came from. Knowledge can be improved when an elder adds context—the earlier version remains in revision history—or forgotten when privacy, cultural restrictions, or consent require withdrawal.

An interactive graph makes relationships tangible: Elder → Location → Category → Memory → Tags. This is not a disposable chatbot. The core product is an evolving, attributable archive that persists between conversations.

Cognee supplies the persistent AI-memory integration boundary. Atomic JSON storage, lexical search, and grounded answer fallbacks keep the full demo working if Cognee, Hugging Face, or Gemini is unavailable. Eight Nepal-focused memories make the experience ready to demonstrate immediately.

## Technologies

FastAPI, Streamlit, Cognee, Gemini (`google-genai`), Hugging Face Sentence Transformers, PyVis, NetworkX, Pydantic, JSON, and Docker Compose.

## Three-minute demo

1. Explain persistent, governable memory on **Home** and load the Nepal dataset.
2. Ask “What did elders teach children?” in **Recall**; reveal the evidence cards.
3. Open **Memory Graph** to explore people, places, traditions, and shared tags.
4. Add a detail in **Improve** and explain preserved revision history.
5. Use **Forget** to demonstrate continuing consent and privacy.
6. Point to the provider modes: the archive remains usable offline.

## Track alignment

The project makes the complete memory lifecycle—remember, recall, improve, and forget—the product foundation. Persistent memory carries cultural knowledge across sessions while preserving provenance and community control.

## What makes it unique

Heritage Memory treats cultural knowledge as governed relational memory, not chatbot context. It combines attribution, revisions, multilingual semantic retrieval, a visible knowledge graph, and consent-aware deletion in one resilient MVP.

## Future improvements

Audio capture and source playback, Nepali and community-language interfaces, steward permissions, controls for sacred or restricted knowledge, contradiction review, encrypted community-owned hosting, and deeper Cognee graph/deletion synchronization.
