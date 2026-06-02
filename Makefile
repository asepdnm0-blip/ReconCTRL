.PHONY: setup run stop restart migrate logs clean

# Default action
all: run

# Setup environment variables
setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example template."; \
	else \
		echo ".env file already exists."; \
	fi

# Build and start services in the background
run: setup
	docker-compose up -d --build
	@echo "Services running. Open http://localhost for Frontend, http://localhost:8000/docs for Swagger API Docs."

# Stop running services
stop:
	docker-compose down

# Restart all services
restart: stop run

# Run database migrations using Alembic inside FastAPI backend
migrate:
	docker-compose exec backend alembic upgrade head

# View real-time logs
logs:
	docker-compose logs -f

# Clean containers and persistent database volumes
clean:
	docker-compose down -v
	@echo "Removed containers, networks, and persistent database volumes."
