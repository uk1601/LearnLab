# Base Image for both Development and Production
FROM python:3.12-slim AS base

WORKDIR /app

# Install system dependencies and Poetry
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry && \
    poetry config virtualenvs.create false

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock ./

# Install common dependencies
RUN poetry install --no-interaction --no-root

# ------------------------------------------
# Development Stage
# ------------------------------------------
FROM base AS development

# Copy application files
COPY . .

# Expose port for development
EXPOSE 8000 5678

# Command for development with hot reload
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ------------------------------------------
# Production Stage
# ------------------------------------------
FROM base AS production

# Copy application files
COPY . .

# Install only production dependencies
RUN poetry install --no-dev --no-interaction

# Create non-root user
RUN addgroup --system appgroup && \
    adduser --system --group appuser && \
    chown -R appuser:appgroup /app

USER appuser

# Expose port for production
EXPOSE 8000

# Optional healthcheck (uncomment to enable)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8000/health || exit 1

# Command for production
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers"]
