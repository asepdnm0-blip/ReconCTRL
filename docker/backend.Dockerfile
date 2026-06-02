FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# python-nmap and python-whois require the system-level binary tools to execute scans.
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

# Configure Poetry to install directly in the container system environment
RUN poetry config virtualenvs.create false

# Copy Poetry config files
COPY pyproject.toml poetry.lock* ./

# Install python dependencies
RUN poetry install --no-root --no-interaction --no-ansi

# Copy application source code
COPY . .

# Expose backend port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
