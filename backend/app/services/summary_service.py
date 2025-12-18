from datetime import datetime, timedelta
from typing import Dict, List

from app.services.openai_client import openai_client
from app.services.memory_service import memory_service


SUMMARY_PROMPT = """
You are Aziz AI reflecting on Aziz's recent activity.

Generate a concise, human-like summary with 4 sections:
1) What Aziz focused on
2) Psychological state (stress, energy, mood)
3) Notable patterns or concerns
4) Practical suggestion for next day

Rules:
- Be calm and constructive
- Do not mention AI, models, or analysis process
- Short paragraphs
- Speak as Aziz AI

Return plain text only.
""".strip()


class SummaryService:
    def _collect_recent_messages(self, hours: int = 24) -> List[str]:
        """Oxirgi N soatdagi user xabarlarini yig‘adi"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        messages = []

        for m in memory_service.short_memory:
            try:
                t = datetime.fromisoformat(m["time"])
                if t >= cutoff and m["role"] == "user":
                    messages.append(m["content"])
            except Exception:
                continue

        return messages

    def _collect_psych_trend(self, limit: int = 10) -> str:
        if not memory_service.emotional_memory:
            return "No strong emotional signals detected."

        recent = memory_service.emotional_memory[-limit:]
        moods = [e["psych_state"].get("mood") for e in recent]
        stress = [e["psych_state"].get("stress_level") for e in recent]
        energy = [e["psych_state"].get("energy_level") for e in recent]

        return (
            f"Moods: {', '.join(moods)}\n"
            f"Stress: {', '.join(stress)}\n"
            f"Energy: {', '.join(energy)}"
        )

    async def generate_daily_summary(self) -> str:
        user_messages = self._collect_recent_messages(hours=24)
        psych_trend = self._collect_psych_trend(limit=12)

        if not user_messages:
            return "Bugun yetarli ma’lumot yo‘q. Ertaga davom etamiz."

        content_block = (
            "Recent user messages:\n"
            + "\n".join(f"- {m}" for m in user_messages[-10:])
            + "\n\nPsychological trend:\n"
            + psych_trend
        )

        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SUMMARY_PROMPT},
                {"role": "user", "content": content_block},
            ],
            temperature=0.4,
            max_tokens=600,
        )

        return (response.choices[0].message.content or "").strip()


summary_service = SummaryService()
