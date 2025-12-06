FROM python:3.11-slim

WORKDIR /app

COPY . /app          # ← rootdagi hamma fayllar, server.py ham kiradi!

RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir -r telegram_bot/requirements.txt

EXPOSE 8000

CMD ["python", "server.py"]
