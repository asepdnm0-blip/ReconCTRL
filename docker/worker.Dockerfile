FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (nmap, whois are required for worker execution)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    nmap \
    whois \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.8.3
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Configure Poetry to install directly in system environment
RUN poetry config virtualenvs.create false

# Copy backend dependencies first to leverage caching
COPY backend/pyproject.toml backend/poetry.lock* ./backend/

# Install python dependencies using backend's pyproject.toml
WORKDIR /app/backend
RUN poetry install --no-root --no-interaction --no-ansi

# Reset workdir to app root and copy source code
WORKDIR /app
COPY backend/ ./backend/
COPY worker/ ./worker/

# Set Python Path so the worker folder can find the backend's 'app' package
ENV PYTHONPATH=/app/backend

# Run Celery worker pointing to the tasks
CMD ["celery", "-A", "worker.tasks.celery_app", "worker", "--loglevel=info"]
