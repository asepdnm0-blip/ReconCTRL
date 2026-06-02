# ReconCTRL Backend

FastAPI application with async SQLAlchemy, Celery, and Redis integration.

## Requirements
- Python 3.11
- Poetry (for dependency management)

## Setup and Development

1. Ensure Poetry is installed:
   ```bash
   pip install poetry
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Enter the virtual environment:
   ```bash
   poetry shell
   ```

4. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## Database Migrations (Alembic)

1. Generate a new migration script:
   ```bash
   alembic revision --autogenerate -m "Initial models"
   ```

2. Run migrations to update the database:
   ```bash
   alembic upgrade head
   ```
