# services/behavior_analyzer.py

from typing import Dict
from app.services.openai_client import openai_client


class BehaviorAnalyzer:
    def __init__(self):
        self.system_prompt = (
            "You are a psychological analyzer. "
            "Analyze the user's message and return ONLY JSON with these fields:\n"
            "- mood: calm | neutral | angry | anxious | motivated | tired\n"
            "- stress_level: low | medium | high\n"
            "- energy_level: low | normal | high\n"
            "- cognitive_load: low | normal | overload\n"
            "- confidence: low | normal | high\n"
            "Do not explain. Do not add text."
        )

    async def analyze(self, user_message: str) -> Dict:
        try:
            response = await openai_client.chat(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
            )

            content = response.strip()

            # Xavfsiz JSON parse
            if content.startswith("{") and content.endswith("}"):
                return eval(content)

        except Exception:
            pass

        # Fallback (har doim tizim yiqilmasligi uchun)
        return {
            "mood": "neutral",
            "stress_level": "medium",
            "energy_level": "normal",
            "cognitive_load": "normal",
            "confidence": "normal",
        }


behavior_analyzer = BehaviorAnalyzer()

