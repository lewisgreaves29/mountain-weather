# Stage 1: Build Vue 3 Frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Python Backend & Dist
FROM python:3.12-alpine AS runner
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    PATH="/app/.venv/bin:$PATH"

# Install system dependencies
RUN apk add --no-cache curl ca-certificates

# Install uv for fast, reliable package operations
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency manifests and sync virtualenv
COPY pyproject.toml uv.lock* ./
RUN if [ -f uv.lock ]; then uv sync --frozen --no-dev --no-install-project; else uv sync --no-dev --no-install-project; fi

# Copy application source & config
COPY backend/ ./backend/
COPY config/ ./config/

# Copy built frontend assets into FastAPI static root
COPY --from=frontend-builder /build/dist ./backend/app/static

# Run as non-privileged user
RUN adduser -D -u 10001 appuser && chown -R appuser:appuser /app
USER 10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
