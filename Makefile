.PHONY: run makemigrations migrate sync lock clean lint format test shell superuser startapp collectstatic docker-up docker-down docker-logs

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------

run:
	uv run python manage.py runserver

shell:
	uv run python manage.py shell_plus

superuser:
	uv run python manage.py createsuperuser

startapp:
	@if [ -z "$(name)" ]; then echo "Usage: make startapp name=blog"; exit 1; fi
	@if [ -d "src/apps/$(name)" ]; then echo "Error: App '$(name)' already exists"; exit 1; fi
	uv run python manage.py startapp $(name) src/apps/$(name)
	@sed -i '' 's/name = "$(name)"/name = "apps.$(name)"/' src/apps/$(name)/apps.py
	@echo "✅ App '$(name)' created in src/apps/$(name)"

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

makemigrations:
	uv run python manage.py makemigrations

migrate:
	uv run python manage.py migrate

# ---------------------------------------------------------------------------
# Static
# ---------------------------------------------------------------------------

collectstatic:
	uv run python manage.py collectstatic --noinput

# ---------------------------------------------------------------------------
# Code quality
# ---------------------------------------------------------------------------

lint:
	uv run ruff check src/

format:
	uv run ruff format src/
	uv run ruff check --fix src/

test:
	uv run pytest

# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------

sync:
	uv sync

lock:
	uv lock

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .ruff_cache
