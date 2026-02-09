# Django Starter Template

Базовый шаблон для быстрого старта новых проектов на Django.

## Особенности

- **`src/`-layout** — исходный код отделён от корня проекта
- **uv** — быстрый менеджер зависимостей (`pyproject.toml` + `uv.lock`)
- **Конфигурация** — `python-decouple` + `.env`
- **Безопасность** — secure-by-default (без дефолтного `SECRET_KEY`, production hardening)
- **Custom User** — `AbstractUser` в `core` из коробки
- **Статика** — WhiteNoise для production serving
- **Docker** — Dockerfile (multi-stage, uv) + docker-compose (PostgreSQL)
- **Инструменты** — ruff, django-extensions, django-debug-toolbar

## Быстрый старт

### Требования

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)
- Make (опционально)

### Установка

```bash
uv sync                         # создаёт .venv + ставит все зависимости
cp .env.example .env            # обязательно — задать SECRET_KEY
make migrate
make run                        # http://127.0.0.1:8000
```

### Docker

```bash
cp .env.example .env
# настроить DATABASE_URL=postgres://django:django@db:5432/django_app
docker compose up -d --build    # web + PostgreSQL
```

## Структура проекта

```
├── manage.py
├── pyproject.toml              # зависимости + ruff config
├── uv.lock                     # lockfile (авто-генерируется)
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── docker-compose.override.yml # dev overrides
└── src/
    ├── apps/
    │   └── core/               # Custom User, базовые модели
    ├── config/
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    ├── static/                 # CSS, JS, images
    ├── media/                  # user uploads
    └── templates/
        └── base.html
```

## Команды Makefile

| Команда              | Описание                          |
|----------------------|-----------------------------------|
| `make run`           | Запуск dev-сервера                |
| `make migrate`       | Создание и применение миграций    |
| `make sync`          | Установка зависимостей (`uv sync`)|
| `make lock`          | Обновить lockfile (`uv lock`)     |
| `make lint`          | Проверка кода (ruff)              |
| `make format`        | Форматирование кода (ruff)        |
| `make shell`         | Django shell_plus                 |
| `make superuser`     | Создать суперпользователя         |
| `make collectstatic` | Сборка статики                    |
| `make docker-up`     | Поднять контейнеры                |
| `make docker-down`   | Остановить контейнеры             |
| `make docker-logs`   | Логи контейнеров                  |
| `make clean`         | Очистка кэша (__pycache__)        |

## Создание нового приложения

```bash
./scripts/startapp.sh blog
```

Создаст `src/apps/blog/` с уже настроенным `apps.py` (`name = "apps.blog"`).
Не забудьте добавить `"apps.blog"` в `INSTALLED_APPS`.
