# Compute version from git tags (e.g., v0.9.0, or commit hash if untagged)
BOUGH_VERSION := $(shell git describe --tags --always --dirty 2>/dev/null || echo "unknown")
export BOUGH_VERSION

.PHONY: dev dev-d dev-down dev-purge prod prod-build prod-down test manage release

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
	docker compose exec api uv run python manage.py $(filter-out $@,$(MAKECMDGOALS))

# Silently ignore any extra targets passed as CLI arguments (e.g., `make manage help`)
%:
	@:

# Build and push release images
release:
	@if [ "$(BOUGH_VERSION)" = "unknown" ] || [[ "$(BOUGH_VERSION)" == *"-dirty"* ]]; then \
		echo "Error: Cannot release an untagged or dirty repository. Please commit and tag first."; \
		exit 1; \
	fi
	docker compose build --provenance=false api web
	docker tag ghcr.io/erfee7/bough-api:$(BOUGH_VERSION) ghcr.io/erfee7/bough-api:latest
	docker tag ghcr.io/erfee7/bough-web:$(BOUGH_VERSION) ghcr.io/erfee7/bough-web:latest
	docker push ghcr.io/erfee7/bough-api:$(BOUGH_VERSION)
	docker push ghcr.io/erfee7/bough-api:latest
	docker push ghcr.io/erfee7/bough-web:$(BOUGH_VERSION)
	docker push ghcr.io/erfee7/bough-web:latest