# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies required by psycopg2-binary and for health checks
RUN apt-get update \ 
    && apt-get install --no-install-recommends -y build-essential libpq-dev curl \ 
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specification and install
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Create a non-root user to run the service
RUN useradd --create-home fastapi

COPY alembic alembic
COPY alembic.ini ./
COPY logging.yaml ./
COPY src src

USER fastapi

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
