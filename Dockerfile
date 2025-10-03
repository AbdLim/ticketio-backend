# 1. Use a lightweight Python base image
FROM python:3.13-slim AS base

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# Install system build deps + Java
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Install UV globally
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

# Copy dependency files and source code for editable install
COPY pyproject.toml uv.lock ./
COPY alembic.ini ./
COPY app ./app
COPY migrations ./migrations
COPY README.md ./

# Install dependencies (editable mode works now)
RUN uv sync --frozen --no-cache

# Check Java version (sanity check, optional — can remove later)
RUN java -version

EXPOSE 8000

# Run Alembic migrations first, then start Uvicorn
CMD ["/bin/sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
