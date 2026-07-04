import os

from backend.models.schemas import Memory


class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    @property
    def mode(self) -> str:
        return "connected" if self.client else "grounded-mock"

    def summarize(self, text: str) -> str:
        if self.client:
            prompt = "Summarize this oral heritage memory respectfully in one sentence. Add no facts:\n" + text
            try:
                return self.client.models.generate_content(model=self.model_name, contents=prompt).text.strip()
            except Exception:
                pass
        clean = " ".join(text.split())
        return clean if len(clean) <= 180 else clean[:177].rsplit(" ", 1)[0] + "…"

    def answer(self, query: str, memories: list[Memory]) -> str:
        if not memories:
            return "I don’t have enough preserved memory to answer that yet. Try remembering a related story first."
        context = "\n\n".join(
            f"Memory {i + 1} — {m.elder_name}, {m.location}: {m.memory_text}"
            for i, m in enumerate(memories)
        )
        if self.client:
            prompt = f"""You are a respectful cultural archivist. Answer the question using ONLY the preserved memories below.
Do not add outside facts or assumptions. If they do not contain the answer, say the preserved memories are insufficient.
Write a clear, warm answer and attribute details to the relevant elder or location.

QUESTION: {query}

PRESERVED MEMORIES:
{context}"""
            try:
                return self.client.models.generate_content(model=self.model_name, contents=prompt).text.strip()
            except Exception:
                pass
        evidence = " ".join(m.summary or m.memory_text for m in memories)
        return f"From the preserved memories: {evidence}"

