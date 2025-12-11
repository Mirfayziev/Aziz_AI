# backend/Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Backend papkasi ichidagi app papkasini konteynerga ko‘chiramiz
COPY app /app/app

# Backend papkasi ichidagi requirements.txt ni ko‘chiramiz
COPY requirements.txt /app/requirements.txt

# Kutubxonalarni o‘rnatamiz
RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

# FastAPI serverni ishga tushiramiz
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
