import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.openai_client import openai_client
from app.services.vector_memory import vector_memory


SHORT_MEMORY_LIMIT = int(os.getenv("AZIZAI_SHORT_MEMORY_LIMIT", "20"))
ENABLE_DEEP_MEMORY = os.getenv("AZIZAI_ENABLE_DEEP_MEMORY", "1") == "1"


class MemoryService:
    def __init__(self) -> None:
        self.short_memory: List[Dict[str, Any]] = []
        self.emotional_memory: List[Dict[str, Any]] = []

        # LLM extractor prompt (faqat user haqida “durable” faktlar)
        self.extractor_prompt = (
            "Extract durable long-term memories about Aziz from the user's message.\n"
            "Return ONLY JSON: {\"facts\": [\"...\", \"...\", ...]}\n"
            "Rules:\n"
            "- Only facts/preferences/goals/habits/constraints that remain useful later.\n"
            "- Max 3 facts.\n"
            "- If nothing durable, return {\"facts\": []}.\n"
            "- No extra text."
        )

    def store_message(
        self,
        role: str,
        content: str,
        psych_state: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.short_memory.append(
            {
                "role": role,
                "content": content,
                "time": datetime.utcnow().isoformat(),
            }
        )
        if len(self.short_memory) > SHORT_MEMORY_LIMIT:
            self.short_memory.pop(0)

        if psych_state:
            self.emotional_memory.append(
                {"psych_state": psych_state, "time": datetime.utcnow().isoformat()}
            )
            if len(self.emotional_memory) > 200:
                self.emotional_memory.pop(0)

    def build_context(self) -> List[Dict[str, str]]:
        ctx: List[Dict[str, str]] = []

        # emotional trend (oxirgi 5)
        if self.emotional_memory:
            recent = self.emotional_memory[-5:]
            trend = ", ".join(
                f"{e['psych_state'].get('mood')}/{e['psych_state'].get('stress_level')}"
                for e in recent
            )
            ctx.append({"role": "system", "content": f"Recent emotional trend: {trend}"})

        # short chat
        ctx.extend({"role": m["role"], "content": m["content"]} for m in self.short_memory)
        return ctx

    async def extract_and_store_facts(self, user_id: str, user_message: str) -> None:
        if not ENABLE_DEEP_MEMORY:
            return

        # juda qisqa xabarlarni factga aylantirmaymiz
        if len((user_message or "").strip()) < 18:
            return

        try:
            resp = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.extractor_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
                max_tokens=180,
            )
            content = (resp.choices[0].message.content or "").strip()
            data = json.loads(content)
            facts = data.get("facts", [])
            if not isinstance(facts, list):
                return

            for f in facts[:3]:
                if isinstance(f, str) and f.strip():
                    await vector_memory.add(
                        user_id=user_id,
                        text=f.strip(),
                        meta={"type": "fact"}
                    )
        except Exception:
            return

    async def retrieve_deep_memories(self, user_id: str, query: str, top_k: int = 6) -> List[str]:
        if not ENABLE_DEEP_MEMORY:
            return []
        try:
            items = await vector_memory.search(user_id=user_id, query=query, top_k=top_k)
            return [i.text for i in items]
        except Exception:
            return []


memory_service = MemoryService()
