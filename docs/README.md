# Django Starter Template

Шаблон для быстрого старта проектов на Django.

`Python 3.13+` · `Django` · `uv` · `Docker` · `PostgreSQL`

## Особенности

- **`src/`-layout** — код отделён от конфигурации
- **[uv](https://docs.astral.sh/uv/)** — быстрый менеджер зависимостей
- **python-decouple** + `.env` — конфигурация через окружение
- **Custom User** (`AbstractUser`) из коробки
- **WhiteNoise** — статика в production без nginx
- **Docker** multi-stage + docker-compose (PostgreSQL 16)
- **[django-unfold](https://github.com/unfoldadmin/django-unfold)** — современная админка
- **ruff**, django-extensions, django-debug-toolbar

## Быстрый старт

```bash
# Клонировать и установить зависимости
git clone https://github.com/your-username/django-starter-template.git my-project
cd my-project
uv sync

# Настроить окружение
cp .env.example .env

# Сгенерировать SECRET_KEY и вставить в .env
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Миграции + суперпользователь
make makemigrations
make migrate
make superuser

# Запуск
make run
```

http://127.0.0.1:8000 — сайт · http://127.0.0.1:8000/admin/ — админка

## Docker

```bash
cp .env.example .env
docker compose up -d --build

docker compose exec web /app/.venv/bin/python manage.py migrate
docker compose exec web /app/.venv/bin/python manage.py createsuperuser
```

Контейнеры: **db** (PostgreSQL 16) + **web** (Django + gunicorn).

Остановить: `docker compose down`

## Структура проекта

```
├── manage.py
├── pyproject.toml
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── src/
    ├── config/                # Настройки Django
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    ├── core/                  # Инфраструктура (НЕ Django-приложение)
    │   ├── models.py
    │   ├── exceptions.py
    │   └── middleware.py
    ├── apps/
    │   └── users/             # Кастомная модель User
    ├── templates/
    │   ├── base.html
    │   └── home.html
    ├── static/
    └── media/
```

## Makefile

| Команда              | Описание                       |
| -------------------- | ------------------------------ |
| `make run`           | Запуск dev-сервера             |
| `make makemigrations`| Создание миграций              |
| `make migrate`       | Применение миграций            |
| `make superuser`     | Создание суперпользователя     |
| `make shell`         | Django shell_plus              |
| `make lint`          | Проверка кода (ruff)           |
| `make format`        | Форматирование кода (ruff)     |
| `make test`          | Запуск тестов (pytest)         |
| `make sync`          | Установка зависимостей         |
| `make lock`          | Обновление lockfile            |
| `make startapp name=blog` | Создание нового приложения |
| `make collectstatic` | Сборка статики                 |
| `make docker-up`     | Запуск контейнеров             |
| `make docker-down`   | Остановка контейнеров          |
| `make docker-logs`   | Просмотр логов                 |
| `make clean`         | Очистка кэша                   |

> Без Make: `make run` → `uv run python manage.py runserver`

## Новое приложение

```bash
make startapp name=blog
```

1. Добавить `"apps.blog"` в `INSTALLED_APPS` в `src/config/settings.py`
2. Подключить URL в `src/config/urls.py`:
   ```python
   path("blog/", include("apps.blog.urls")),
   ```

## Переменные окружения

| Переменная               | По умолчанию           | Описание            |
| ------------------------ | ---------------------- | ------------------- |
| `SECRET_KEY`             | —                      | **Обязательно**     |
| `DEBUG`                  | `False`                | Режим отладки       |
| `ALLOWED_HOSTS`          | —                      | Через запятую       |
| `DATABASE_URL`           | `sqlite:///db.sqlite3` | URL базы данных     |
| `CSRF_TRUSTED_ORIGINS`   | —                      | Через запятую       |
| `LOG_LEVEL`              | `INFO`                 | Уровень логирования |

## FAQ

<details>
<summary><b>Как добавить зависимость?</b></summary>

```bash
uv add django-rest-framework
```
</details>

<details>
<summary><b>Как обновить все зависимости?</b></summary>

```bash
uv lock --upgrade && uv sync
```
</details>

<details>
<summary><b>Зачем Custom User?</b></summary>

Django [рекомендует](https://docs.djangoproject.com/en/stable/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project) создавать кастомную модель User в начале проекта — изменить позже крайне сложно.
</details>

<details>
<summary><b>Зачем WhiteNoise?</b></summary>

Раздача статики в production без nginx/CDN.
</details>

<details>
<summary><b>Почему <code>src/</code> layout?</b></summary>

Отделяет код от конфигурации в корне. Стандартная практика для Python-проектов.
</details>

<details>
<summary><b>Почему <code>uv.lock</code> не в репозитории?</b></summary>

Шаблон намеренно не коммитит `uv.lock`, чтобы при клонировании `uv sync` устанавливал актуальные версии зависимостей. **После** того как вы начали строить свой проект на основе шаблона, рекомендуется убрать `uv.lock` из `.gitignore` и закоммитить его — это обеспечит reproducible builds.
</details>

## Документация

- [Архитектура проекта](architecture.md)
- [Руководство для разработчиков](CONTRIBUTING.md)
- **ADR (Architecture Decision Records):**
  - [001 — src/-layout](adr/001-src-layout.md)
  - [002 — Кастомная модель User](adr/002-custom-user-model.md)
  - [003 — UUID первичные ключи](adr/003-uuid-primary-keys.md)
  - [004 — Сервисный слой](adr/004-service-layer.md)
