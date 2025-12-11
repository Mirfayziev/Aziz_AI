FROM python:3.12-slim

WORKDIR /app

# Copy app folder completely
COPY ./app /app

# Install requirements from app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose port
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
