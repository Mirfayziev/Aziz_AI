import json
from typing import Dict

from app.services.openai_client import openai_client


class BehaviorAnalyzer:
    def __init__(self) -> None:
        self.system_prompt = (
            "Return ONLY valid minified JSON.\n"
            "Fields:\n"
            "mood: calm|neutral|angry|anxious|motivated|tired\n"
            "stress_level: low|medium|high\n"
            "energy_level: low|normal|high\n"
            "cognitive_load: low|normal|overload\n"
            "confidence: low|normal|high\n"
            "No extra keys. No explanations."
        )

    async def analyze(self, user_message: str) -> Dict:
        fallback = {
            "mood": "neutral",
            "stress_level": "medium",
            "energy_level": "normal",
            "cognitive_load": "normal",
            "confidence": "normal",
        }

        try:
            resp = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
                max_tokens=120,
            )
            content = (resp.choices[0].message.content or "").strip()
            data = json.loads(content)

            # hard validation (xato bo‘lsa fallback)
            for k in fallback.keys():
                if k not in data:
                    return fallback
            return {k: data[k] for k in fallback.keys()}
        except Exception:
            return fallback


behavior_analyzer = BehaviorAnalyzer()
