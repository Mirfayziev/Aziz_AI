# Aziz AI — Deployment (Backend + Telegram Bot)

## 1) Backend service (AzizAi)
- Root directory: `backend`
- Start command:
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Backend Variables (Railway)
- `OPENAI_API_KEY`
- `DATABASE_URL` (optional; sqlite default works for testing)
- `WEATHER_API_KEY` (OpenWeather)
- `NEWS_API_KEY` (NewsAPI.org)
- `CURRENCY_PROVIDER` = `cbu` (recommended) or `exchangerate`
- Optional:
  - `WEATHER_DEFAULT_CITY`
  - `NEWS_DEFAULT_QUERY`
  - `NEWS_LANG`
  - `MAX_NEWS_ITEMS`

## 2) Telegram bot service (observant-fascination)
- Root directory: `telegram_bot`
- Start command:
  `uvicorn bot:app --host 0.0.0.0 --port $PORT`

### Bot Variables (Railway)
- `TELEGRAM_BOT_TOKEN`
- `BACKEND_URL` = your backend public url (example: `https://azizai-production.up.railway.app`)
- Optional: `SEND_VOICE_DEFAULT` = `1` or `0`

## 3) Set Telegram Webhook
Webhook URL:
`https://<telegram-bot-domain>/webhook`

Example:
`https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://observant-fascination-production-6461.up.railway.app/webhook`

## 4) Test
- Backend: `/docs`
- Telegram: `/start`, then `ob-havo`, `valyuta`, `yangilik`, and normal chat.
