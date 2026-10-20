FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends nmap \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY CLI ./CLI
COPY database ./database
COPY systems ./systems
COPY tools ./tools
COPY src ./src

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    DATABASE=sqlite+aiosqlite:///./data/data.db

CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
