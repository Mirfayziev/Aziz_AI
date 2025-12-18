# backend/app/services/summary_service.py

from typing import List
from datetime import date

from app.services.openai_client import openai_client


class SummaryService:
    async def generate_daily_summary(self) -> str:
        today = date.today().isoformat()

        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Summarize the user's day briefly and clearly. No AI mentions.",
                },
                {
                    "role": "user",
                    "content": f"Summarize activity for {today}",
                },
            ],
            temperature=0.3,
            max_tokens=300,
        )

        return response.choices[0].message.content.strip()

    async def generate_weekly_summary(self) -> str:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Provide a concise weekly summary. No AI mentions.",
                }
            ],
            temperature=0.3,
            max_tokens=400,
        )

        return response.choices[0].message.content.strip()


# ✅ SINGLETON (TO‘G‘RI USUL)
summary_service = SummaryService()
