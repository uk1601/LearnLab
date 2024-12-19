# Use the same base image as in docker-compose
FROM apache/airflow:2.10.3

USER root

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VERSION=1.7.1
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=$POETRY_HOME python3 - --version $POETRY_VERSION \
    && chmod a+x /opt/poetry/bin/poetry

# Switch to airflow user for subsequent operations
USER airflow

# Copy poetry files
COPY --chown=airflow:root pyproject.toml poetry.lock /opt/airflow/

# Configure poetry and install dependencies
WORKDIR /opt/airflow
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the rest of the application
COPY --chown=airflow:root . /opt/airflow/