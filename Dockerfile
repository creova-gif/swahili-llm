# Stage 1: Build & dependencies
FROM python:3.15-slim AS builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# Stage 2: Final non-root runtime image
FROM python:3.15-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 lughallm \
    && useradd --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin lughallm

COPY --from=builder /install /usr/local
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

COPY . /app
RUN chown -R lughallm:lughallm /app

USER lughallm

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "lughallm.src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
