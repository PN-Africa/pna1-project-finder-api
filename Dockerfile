# syntax=docker/dockerfile:1

# ==============================================================================
# Production Dockerfile for Project Finder (PNA 1)
# Runtime: Python 3.14 with uv package manager
# ==============================================================================

FROM python:3.14-slim AS base

# Prevent Python from writing pyc files and keep stdout/stderr unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    DJANGO_SETTINGS_MODULE=projectfinder.settings.prod \
    PORT=8000

WORKDIR /app

# Install system dependencies
# - libpq5: runtime library for PostgreSQL / Supabase
# - curl & ca-certificates: healthcheck probe and secure outbound connections
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy uv package manager binaries from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies first (leverages layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source code
COPY . /app

# Install project package into the virtualenv
RUN uv sync --frozen --no-dev

# Place virtual environment binaries in system PATH
ENV PATH="/app/.venv/bin:$PATH"

# Pre-collect static files during build time
# Uses a build-time placeholder key; no database connection is required
RUN DJANGO_SECRET_KEY=build-time-secret-placeholder-for-collectstatic \
    python manage.py collectstatic --noinput

# Make entrypoint executable, set up directories, and configure non-root user
RUN chmod +x /app/entrypoint.sh && \
    useradd -u 1000 -m -s /bin/bash appuser && \
    mkdir -p /app/staticfiles /app/media && \
    chown -R appuser:appuser /app

# Run as non-privileged user
USER appuser

# Expose HTTP port
EXPOSE 8000

# Container healthcheck using the lightweight health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/health/ || exit 1

# Entrypoint script runs migrations and optional runtime hooks
ENTRYPOINT ["/app/entrypoint.sh"]

# Default production server command
CMD ["gunicorn", "projectfinder.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
