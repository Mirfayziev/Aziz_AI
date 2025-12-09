# Aziz AI Pro — Backend + Telegram Bot (ZIP tayyor)

Bu loyiha ikki qismdan iborat:

- `backend/` — FastAPI asosidagi Aziz AI backend:
  - `/api/chat` — chat + vector memory + profiling bilan
  - `/api/audio/*` — ovozni matnga va AI javobga
  - `/api/profile/*` — bio / goals / interests
  - `/api/planner/*` — kundalik reja

- `telegram_bot/` — Telegram webhook bot:
  - Matnli xabarlar → `/api/chat` ga
  - Ovozli xabarlar → `/api/audio/chat` ga

## Deploy (Railway)

### Backend servisi

- Root folder: `backend`
- Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

- Env (Variables):

```bash
OPENAI_API_KEY=...
DATABASE_URL=sqlite:///./aziz_ai.db  # yoki PostgreSQL URL
MODEL_FAST=gpt-4o-mini
MODEL_DEFAULT=gpt-4o
MODEL_DEEP=o1-mini
EMBEDDING_MODEL=text-embedding-3-small
```

### Telegram bot servisi

- Root folder: `telegram_bot`
- Start command:

```bash
uvicorn server:app --host 0.0.0.0 --port $PORT
```

- Env:

```bash
TELEGRAM_BOT_TOKEN=...
AZIZ_BACKEND_CHAT_URL=https://<backend-domain>/api/chat
AZIZ_BACKEND_AUDIO_URL=https://<backend-domain>/api/audio
```

Keyin webhook o'rnatish:

```bash
https://api.telegram.org/bot<token>/setWebhook?url=https://<bot-domain>/webhook
```
