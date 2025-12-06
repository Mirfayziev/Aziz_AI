FROM python:3.11-slim

WORKDIR /app

# requirements o‘rnatish uchun butun root papkani ko‘chiramiz
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "server.py"]
