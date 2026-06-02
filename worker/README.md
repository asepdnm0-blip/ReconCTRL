# ReconCTRL Celery Worker

This service processes async background jobs (Nmap port scans, WHOIS lookups) for ReconCTRL. It shares the codebase with the `backend/` package.

## Local Execution

To run the worker locally, you must use the backend's Poetry virtual environment since all dependencies and task logic are defined there:

1. Navigate to the `backend/` directory and activate the virtual environment:
   ```bash
   cd ../backend
   poetry shell
   ```

2. Run the Celery worker process pointing to the `worker.tasks` entry point:
   ```bash
   celery -A worker.tasks.celery_app worker --loglevel=info
   ```

Note: Make sure Redis is running and the `REDIS_URL` environment variable is configured.
