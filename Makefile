.PHONY: run migrate sync lock clean lint format shell superuser collectstatic docker-up docker-down docker-logs

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------

run:
	uv run python manage.py runserver

shell:
	uv run python manage.py shell_plus

superuser:
	uv run python manage.py createsuperuser

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

migrate:
	uv run python manage.py makemigrations
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
