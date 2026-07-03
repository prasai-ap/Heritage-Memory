import logging
import os

from backend.models.schemas import Memory

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        self.mode = "gemini" if self.api_key else "mock"

    async def answer(self, question: str, memories: list[Memory]) -> str:
        if not memories:
            return "I could not find a preserved memory related to that question yet."
        context = "\n\n".join(
            f"[{m.id}] {m.elder_name} from {m.location} ({m.category}): {m.memory_text}"
            for m in memories
        )
        if self.api_key:
            try:
                from google import genai

                client = genai.Client(api_key=self.api_key)
                response = await client.aio.models.generate_content(
                    model=self.model,
                    contents=(
                        "You are a careful cultural heritage guide. Answer only from the preserved "
                        "oral memories below. Attribute knowledge to the elder and place when useful, "
                        "respect uncertainty, and do not invent details.\n\n"
                        f"QUESTION: {question}\n\nMEMORIES:\n{context}"
                    ),
                )
                if response.text:
                    return response.text
            except Exception as exc:
                logger.warning("Gemini failed; using grounded local response: %s", exc)
                self.mode = "mock"
        first = memories[0]
        return (
            f"According to {first.elder_name} from {first.location}, {first.memory_text} "
            f"This is preserved as a {first.category.lower()} memory."
        )
