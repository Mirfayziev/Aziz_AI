from openai import OpenAI
import os

client = OpenAI()

MODEL_DEFAULT = os.getenv("MODEL_DEFAULT", "gpt-4.1")
MODEL_FAST = os.getenv("MODEL_FAST", "gpt-4o-mini")
MODEL_DEEP = os.getenv("MODEL_DEEP", "o1")

def get_model(tier: str):
    if tier == "fast":
        return MODEL_FAST
    if tier == "deep":
        return MODEL_DEEP
    return MODEL_DEFAULT


def generate_plan(query: str, model_tier: str = "default"):
    model = get_model(model_tier)

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Siz Aziz AI planner modulisiz. "
                    "Foydalanuvchi 'bugungi reja', 'ertangi ishlar', 'haftalik reja', "
                    "'oylik strategiya' kabi qisqa buyruqlar bersa, "
                    "siz darhol professional, strukturali va amaliy reja tuzasiz. "
                    "Hech qachon savol qaytarmang. "
                    "Har doim to‘g‘ridan-to‘g‘ri reja bilan javob bering."
                )
            },
            {"role": "user", "content": query}
        ]
    )

    return completion.choices[0].message.content
