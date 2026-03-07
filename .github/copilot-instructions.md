# Copilot Instructions — Django Starter Template

## Architecture

This is a Django project using `src/`-layout: all Python source code lives under `src/`, separated from root config files (`manage.py`, `pyproject.toml`, `Dockerfile`, etc.).

- **`src/config/`** — Django settings, root URL conf (`config.urls`), WSGI/ASGI entry points.
- **`src/core/`** — Infrastructure package (**not** a Django app). Houses cross-cutting concerns: `BaseModel`, exceptions, middleware, utilities. Import as `core.*`.
- **`src/apps/`** — Django apps. Each app is referenced as `apps.<name>` (e.g. `apps.users`).
- **`src/templates/`** — Project-level templates. `base.html` provides the layout shell.
- **`src/static/`** — Project-level static assets (`css/`, `js/`, `images/`).
- **`src/media/`** — User-uploaded files (not committed).

`manage.py` adds `src/` to `sys.path`, so imports use `apps.*`, `config.*`, and `core.*` — never `src.apps.*`.

### core/ vs apps/ — what goes where

| `src/core/` (infrastructure) | `src/apps/<name>/` (business logic) |
|---|---|
| `BaseModel` (abstract), exceptions, middleware | Models, views, serializers, admin |
| Shared utilities, helpers | App-specific URLs, templates |
| No migrations, no Django AppConfig | Has `apps.py`, registered in `INSTALLED_APPS` |
| Imported as `core.models`, `core.exceptions` | Imported as `apps.<name>.models` |

## Key Conventions

### Custom User Model
`AUTH_USER_MODEL = "users.User"` — a custom `AbstractUser` subclass in `src/apps/users/models.py`. All user-related fields go here. Never use `django.contrib.auth.models.User` directly.

### BaseModel
All new models (except User) should inherit from `core.models.BaseModel`, which provides UUID primary key, `created_at`, and `updated_at` fields.

### Creating a New App
```bash
make startapp name=<appname>
```
This creates the app in `src/apps/<appname>/` and patches `apps.py` to set `name = "apps.<appname>"`. After creation:
1. Add `"apps.<appname>"` to `INSTALLED_APPS` in `src/config/settings.py`
2. Wire URLs in `src/config/urls.py`: `path("<appname>/", include("apps.<appname>.urls"))`

### Admin
Uses **django-unfold** — admin classes must inherit from `unfold.admin.ModelAdmin` (not plain `admin.ModelAdmin`). See `src/apps/users/admin.py` for the pattern with `UserAdmin`.

### Configuration & Environment
Settings use **python-decouple** (`config()`) — not `os.environ`. Database URL is parsed via `dj-database-url`. Key env vars: `SECRET_KEY` (required), `DEBUG`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `LOG_LEVEL`.

### Static Files
**WhiteNoise** serves static files in production. Storage backend: `CompressedManifestStaticFilesStorage`. Dev static source: `src/static/`; collected to root `static/`.

### Dev-only Apps
`django-extensions` and `django-debug-toolbar` are conditionally added to `INSTALLED_APPS` only when `DEBUG=True` and the packages are importable (see `src/config/settings.py`).

## Developer Workflow

| Task | Command |
|---|---|
| Install deps | `uv sync` |
| Run dev server | `make run` |
| Create migrations | `make makemigrations` |
| Apply migrations | `make migrate` |
| Django shell | `make shell` (uses `shell_plus`) |
| Lint | `make lint` |
| Format | `make format` |
| Run tests | `make test` |
| Add dependency | `uv add <package>` |
| Docker up | `make docker-up` |

All commands use **uv** as the package manager (not pip). Run Django management commands via `uv run python manage.py ...`.

## Code Quality

- **Ruff** for linting and formatting. Config in `pyproject.toml`: line-length 120, Python 3.13 target, rules `E, F, I, B, UP, DJ`. Migrations are excluded.
- Import sorting: `apps`, `config`, and `core` are `known-first-party`.

## Docker

Multi-stage `Dockerfile`: builder installs deps with `uv sync --no-dev --group prod`, runtime runs **gunicorn** with `--chdir src`. `docker-compose.yml` provides PostgreSQL 16 + web. `docker-compose.override.yml` adds dev overrides (volume mounts, `DEBUG=True`, runserver).

## Production Security

When `DEBUG=False`, settings auto-enable: `SECURE_SSL_REDIRECT`, HSTS (1 year + preload), secure cookies. No manual toggle needed.
