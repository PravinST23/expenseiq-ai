# ExpenseIQ Backend - FastAPI + Tesseract OCR
FROM python:3.10-slim

# Tesseract OCR system binary (pytesseract shells out to it)
RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads/receipts

EXPOSE 8000

# Run migrations then start the API - keeps the container
# self-sufficient for a fresh Postgres instance.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
