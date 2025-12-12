import os
import json
import time
import logging
from typing import Any, Dict, List, Optional

import httpx
from openai import OpenAI

log = logging.getLogger("assistant_service")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
OPENAI_TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
OPENAI_TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "alloy")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "Sen Aziz AI ekansan — foydalanuvchining shaxsiy klonisan. "
    "O‘zingni OpenAI, ChatGPT deb tanishtirma. "
    "Javoblar aniq, amaliy, qisqa va ishonchli bo‘lsin. "
    "Agar savol real vaqt / yangilik / fakt tekshirish talab qilsa, internetdan qidirishni ishga tushir. "
    "Topilgan manbalarni qisqacha keltir (1-3 ta). "
    "Agar internet topilmasa, aniq ayt: 'internetdan topilmadi' va eng yaqin foydali yo‘lni ko‘rsat."
)

# --------------------------
# Web search (Serper / Google)
# --------------------------
async def serper_search(query: str, num: int = 5) -> List[Dict[str, str]]:
    """
    Returns list of {title, link, snippet}
    """
    if not SERPER_API_KEY:
        return []

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"q": query, "num": max(3, min(num, 10))}
    async with httpx.AsyncClient(timeout=20) as client_http:
        r = await client_http.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()

    results = []
    for item in (data.get("organic") or [])[:num]:
        results.append(
            {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            }
        )
    return results


def _should_web_search(message: str) -> bool:
    """
    Fast heuristic to avoid paying search for obvious non-search queries.
    The LLM will also decide via tool call.
    """
    m = message.lower()
    keywords = [
        "bugun", "hozir", "so'nggi", "yangilik", "news", "kurs", "valyuta",
        "ob-havo", "weather", "narx", "price", "qachon", "2025", "2026",
        "manba", "link", "isbot", "tasdiq", "rasmiy",
    ]
    return any(k in m for k in keywords)


async def web_lookup_context(message: str) -> Dict[str, Any]:
    """
    Uses LLM to generate a focused search query, then searches web, returns context.
    """
    # 1) Ask LLM to generate the best search query
    tool_schema = {
        "name": "web_search",
        "description": "Search the web for up-to-date facts and sources.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "description": "Number of results", "default": 5},
            },
            "required": ["query"],
        },
    }

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]

    # Give model option to call tool
    resp = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=messages,
        tools=[{"type": "function", "function": tool_schema}],
        tool_choice="auto",
        temperature=0.2,
    )

    tool_calls = resp.choices[0].message.tool_calls or []
    if not tool_calls:
        # No tool call; still do heuristic search if needed
        if _should_web_search(message) and SERPER_API_KEY:
            query = message
            results = await serper_search(query, num=5)
            return {"query": query, "results": results}
        return {"query": None, "results": []}

    # Execute the tool call (we only support web_search)
    tc = tool_calls[0]
    args = json.loads(tc.function.arguments or "{}")
    query = (args.get("query") or message).strip()
    num_results = int(args.get("num_results") or 5)
    results = await serper_search(query, num=num_results)

    return {"query": query, "results": results}


def _format_sources(results: List[Dict[str, str]], max_items: int = 3) -> str:
    items = []
    for r in results[:max_items]:
        title = r.get("title", "").strip()
        link = r.get("link", "").strip()
        snippet = r.get("snippet", "").strip()
        if not (title or link or snippet):
            continue
        items.append(f"- {title}\n  {link}\n  {snippet}")
    return "\n".join(items).strip()


def _final_answer_with_sources(message: str, web_ctx: Dict[str, Any]) -> str:
    """
    Uses LLM to produce final answer using web context when available.
    """
    results = web_ctx.get("results") or []
    sources_block = _format_sources(results, max_items=3)

    if results:
        user_prompt = (
            "Savol: " + message + "\n\n"
            "Internetdan topilgan kontekst (manbalar):\n"
            f"{sources_block}\n\n"
            "Vazifa:\n"
            "1) Javobni aniq, amaliy va qisqa yoz.\n"
            "2) Agar raqam/fakt bo‘lsa, manbaga tayangan holda ayt.\n"
            "3) Oxirida 1-3 ta manbani (link) alohida qatorda ber.\n"
        )
    else:
        user_prompt = (
            "Savol: " + message + "\n\n"
            "Internetdan kontekst topilmadi yoki search o‘chirilgan.\n"
            "Vazifa:\n"
            "1) Agar aniq real-time fakt kerak bo‘lsa, 'internetdan topilmadi' deb halol ayt.\n"
            "2) Shunga qaramay foydali yo‘l-yo‘riq, tekshirish usuli, alternativ manbalar ayt.\n"
        )

    resp = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.35,
    )
    return resp.choices[0].message.content.strip()


def _tts_to_audio_hex(text: str) -> Optional[str]:
    """
    Converts text to OGG audio bytes using OpenAI TTS and returns hex string.
    If TTS fails, returns None (text still returned).
    """
    try:
        # Shorten extremely long TTS inputs (avoid timeouts)
        tts_text = text.strip()
        if len(tts_text) > 1200:
            tts_text = tts_text[:1200].rsplit(" ", 1)[0] + "..."

        speech = client.audio.speech.create(
            model=OPENAI_TTS_MODEL,
            voice=OPENAI_TTS_VOICE,
            input=tts_text,
            format="ogg",
        )
        audio_bytes = speech.read()
        return audio_bytes.hex()
    except Exception as e:
        log.exception("TTS failed: %s", e)
        return None


# =========================================================
# PUBLIC ENTRYPOINT (use this from router)
# Expected request shape:
#   - external_id: str
#   - message: str
#   - want_voice: bool (optional)
# =========================================================
async def assistant_message_handler(external_id: str, message: str, want_voice: bool = True) -> Dict[str, Any]:
    """
    This is the "miyya" entrypoint.
    Returns:
      { ok: bool, text: str, audio_hex?: str, tool?: str }
    """
    t0 = time.time()

    # 1) Decide + fetch web context (if needed)
    web_ctx = await web_lookup_context(message)
    used_search = bool(web_ctx.get("results"))

    # 2) Final answer (with sources when available)
    text = _final_answer_with_sources(message, web_ctx)

    # 3) TTS (optional)
    audio_hex = None
    if want_voice:
        audio_hex = _tts_to_audio_hex(text)

    dt = round(time.time() - t0, 3)
    return {
        "ok": True,
        "external_id": external_id,
        "tool": "web_search" if used_search else "chat_only",
        "latency_s": dt,
        "text": text,
        "audio_hex": audio_hex,
    }
