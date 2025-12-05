from openai import OpenAI
import os

client = OpenAI()

MODEL_DEFAULT = os.getenv("MODEL_DEFAULT", "gpt-4.1")
MODEL_FAST = os.getenv("MODEL_FAST", "gpt-4o-mini")
MODEL_DEEP = os.getenv("MODEL_DEEP", "o1")


def get_model_by_tier(tier: str):
    if tier == "fast":
        return MODEL_FAST
    if tier == "deep":
        return MODEL_DEEP
    return MODEL_DEFAULT


def create_chat_reply(message: str, model_tier: str = "default"):
    model = get_model_by_tier(model_tier)

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Siz Aziz AI. Siz ChatGPT 5.1 darajasidagi suniy intellektsiz. "
                    "Siz 2025–2030 yillar haqidagi zamonaviy ma'lumotlar bilan ishlaysiz."
                )
            },
            {"role": "user", "content": message}
        ]
    )

    return completion.choices[0].message.content
