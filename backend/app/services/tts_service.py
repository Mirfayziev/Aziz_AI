import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

async def text_to_speech(text: str, output_path: str):
    response = openai.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )

    with open(output_path, "wb") as f:
        f.write(response)
