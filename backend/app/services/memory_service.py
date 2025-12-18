# services/memory_service.py

from typing import List, Dict
from datetime import datetime

# Hozircha RAM / SQLite o‘rniga in-memory (keyin DBga oson ko‘chadi)
SHORT_MEMORY_LIMIT = 20


class MemoryService:
    def __init__(self):
        self.short_memory: List[Dict] = []
        self.long_memory: List[str] = []
        self.emotional_memory: List[Dict] = []

    def store_message(
        self,
        role: str,
        content: str,
        psych_state: Dict | None = None,
    ):
        self.short_memory.append(
            {
                "role": role,
                "content": content,
                "time": datetime.utcnow().isoformat(),
            }
        )

        if psych_state:
            self.emotional_memory.append(
                {
                    "psych_state": psych_state,
                    "time": datetime.utcnow().isoformat(),
                }
            )

        if len(self.short_memory) > SHORT_MEMORY_LIMIT:
            self.short_memory.pop(0)

    def remember_fact(self, fact: str):
        if fact not in self.long_memory:
            self.long_memory.append(fact)

    def build_context(self) -> List[Dict]:
        context: List[Dict] = []

        # Long-term memory
        if self.long_memory:
            context.append(
                {
                    "role": "system",
                    "content": "Known facts about the user:\n"
                    + "\n".join(f"- {f}" for f in self.long_memory),
                }
            )

        # Emotional trend (oxirgi 5 ta)
        if self.emotional_memory:
            recent = self.emotional_memory[-5:]
            summary = ", ".join(
                f"{e['psych_state'].get('mood')}/{e['psych_state'].get('stress_level')}"
                for e in recent
            )
            context.append(
                {
                    "role": "system",
                    "content": f"Recent emotional trend: {summary}",
                }
            )

        # Short-term chat
        context.extend(
            {"role": m["role"], "content": m["content"]}
            for m in self.short_memory
        )

        return context


memory_service = MemoryService()
