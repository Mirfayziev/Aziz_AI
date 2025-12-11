FROM python:3.12-slim

WORKDIR /app

# backend ichidagi requirements.txt ni ko'chiramiz
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

# Backend kodini ko'chiramiz
COPY . /app

EXPOSE 8000

CMD ["python", "server.py"]
