# ReconCTRL Monorepo

ReconCTRL is an automated security reconnaissance orchestration system. It consists of a React frontend, an asynchronous FastAPI backend, and a Celery background worker connected to a PostgreSQL database and Redis broker.

## Project Structure

```
reconctrl/
├── frontend/                     # React 18 + Vite + TailwindCSS
├── backend/                      # FastAPI + Python 3.11 + Poetry
├── worker/                       # Celery worker (shares backend codebase)
├── docker/                       # Dockerfiles per service
│   ├── frontend.Dockerfile
│   ├── backend.Dockerfile
│   └── worker.Dockerfile
├── docker-compose.yml            # Docker orchestration
├── .env.example                  # Template environment variables
└── README.md                     # Monorepo documentation
```

## Quick Start (with Docker Compose)

To spin up the entire application stack including databases and workers, follow these steps:

1. **Clone and Navigate**:
   Go to your workspace root directory.

2. **Prepare Environment File**:
   Copy the example environment variables to create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   Feel free to edit the parameters inside `.env` to suit your development requirements.

3. **Orchestrate Stack**:
   Start the services using Docker Compose (this automatically builds the Dockerfiles located in `/docker`):
   ```bash
   docker-compose up --build
   ```

4. **Initialize Database Tables**:
   Run database migrations using Alembic inside the running backend container:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Exposed Services**:
   - **Frontend UI**: `http://localhost` (exposes React static site served by Nginx)
   - **FastAPI API**: `http://localhost:8000` (exposes backend endpoints)
   - **API Documentation**: `http://localhost:8000/docs` (Swagger Interactive API Documentation)

## Local Development (No Docker)

If you prefer running services individually outside of containers:

### 1. Database and Broker Setup
You will need a PostgreSQL database and a Redis instance running locally:
- Update your `.env` file to point `DATABASE_URL` and `REDIS_URL` to `localhost` instead of their docker container names (`db`, `redis`).

### 2. Frontend Local Server
1. Navigate into the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   pnpm install
   # or
   npm install
   ```
3. Run the development server (Vite):
   ```bash
   pnpm run dev
   # or
   npm run dev
   ```

### 3. Backend Local Server
1. Navigate into the backend folder:
   ```bash
   cd backend
   ```
2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```
3. Spawn shell env and run FastAPI reload server:
   ```bash
   poetry shell
   uvicorn app.main:app --reload --port 8000
   ```

### 4. Celery Worker Local Server
1. Ensure you have activated the backend's Poetry virtual environment.
2. Navigate into the worker folder:
   ```bash
   cd worker
   ```
3. Start the Celery worker process:
   ```bash
   celery -A tasks.celery_app worker --loglevel=info
   ```
