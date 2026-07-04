.PHONY: dev dev-build dev-down prod prod-build prod-down

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