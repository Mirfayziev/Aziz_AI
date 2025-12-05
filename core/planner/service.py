from core.openai_client import ai_generate_plan


async def generate_daily_plan(goals: str, tasks: list):
    prompt = f"""
    Men bugun bajarishim kerak bo'lgan vazifalar: {tasks}
    Mening bugungi maqsadlarim: {goals}

    Iltimos, menga to'liq strukturali kunlik reja tuzib bering.
    """

    result = await ai_generate_plan(prompt)
    return result


async def summarize_day(activities: str):
    prompt = f"""
    Bugungi faoliyatlarim:
    {activities}

    Iltimos, qisqa kundalik xulosa va ertangi kun uchun tavsiyalar bering.
    """

    return await ai_generate_plan(prompt)

def generate_plan(text: str):
    """
    Hozircha demo funksiya.
    Keyin ChatGPT / Aziz AI modeliga ulaymiz.
    """
    return {
        "input": text,
        "plan": [
            "1) Vazifa bo‘yicha ustuvorlik belgilandi",
            "2) Amalga oshirish bosqichlari tuzildi",
            "3) Deadlinelar belgilandi"
        ],
        "status": "draft"
    }
