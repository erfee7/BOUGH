.PHONY: dev dev-d dev-down dev-purge prod prod-build prod-down test manage

# Start dev environment
dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Start dev environment in background
dev-d:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

# Tear down dev environment
dev-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

# Tear down dev environment AND delete the database volume
dev-purge:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down -v

# Build prod images
prod-build:
	docker compose build

# Start prod environment
prod:
	docker compose up -d --build

# Tear down prod environment
prod-down:
	docker compose down

# Run automated tests (api)
test:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm api uv run pytest -v

# Run account management script
manage:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec api uv run python manage.py $(filter-out $@,$(MAKECMDGOALS))

# Silently ignore any extra targets passed as CLI arguments (e.g., `make manage help`)
%:
	@: