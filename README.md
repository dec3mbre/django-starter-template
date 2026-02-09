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

---

## Быстрый старт (пошагово)

### 1. Установить зависимости

Для работы нужен Python 3.13+ и [uv](https://docs.astral.sh/uv/) — быстрый менеджер пакетов для Python.

**Установка uv** (если ещё не установлен):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# или через Homebrew
brew install uv
```

### 2. Клонировать шаблон и установить зависимости

```bash
git clone https://github.com/your-username/django-starter-template.git my-project
cd my-project
uv sync
```

`uv sync` автоматически:
- создаст виртуальное окружение (`.venv/`)
- установит все зависимости из `pyproject.toml`
- сгенерирует `uv.lock` (lockfile для воспроизводимости)

### 3. Настроить переменные окружения

```bash
cp .env.example .env
```

Откройте `.env` и задайте `SECRET_KEY` — это обязательно. Сгенерировать ключ:

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Скопируйте результат в `.env`:

```
SECRET_KEY=ваш-сгенерированный-ключ
```

Остальные настройки в `.env` можно оставить по умолчанию для разработки.

### 4. Применить миграции

```bash
make migrate
# или без Make:
uv run python manage.py makemigrations
uv run python manage.py migrate
```

Это создаст базу данных (SQLite по умолчанию) и все нужные таблицы, включая кастомную модель `User`.

### 5. Создать суперпользователя (для доступа в админку)

```bash
make superuser
# или:
uv run python manage.py createsuperuser
```

### 6. Запустить dev-сервер

```bash
make run
# или:
uv run python manage.py runserver
```

Откройте http://127.0.0.1:8000 — увидите стартовую страницу.
Админка: http://127.0.0.1:8000/admin/

---

## Запуск через Docker

Docker полезен, когда нужна PostgreSQL или окружение, близкое к production.

### Требования

- [Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)

### Запуск

```bash
cp .env.example .env
docker compose up -d --build
```

Это поднимет два контейнера:
- **db** — PostgreSQL 16
- **web** — Django dev-server с hot reload

Сайт доступен на http://127.0.0.1:8000

### Миграции и суперпользователь в Docker

```bash
docker compose exec web /app/.venv/bin/python manage.py migrate
docker compose exec web /app/.venv/bin/python manage.py createsuperuser
```

### Остановить

```bash
make docker-down
# или:
docker compose down
```

---

## Структура проекта

```
├── manage.py                   # точка входа Django
├── pyproject.toml              # зависимости + конфиг ruff
├── uv.lock                     # lockfile (коммитится в git)
├── Makefile                    # команды для разработки
├── .env.example                # шаблон переменных окружения
├── Dockerfile                  # production-образ
├── docker-compose.yml          # Docker: web + PostgreSQL
├── docker-compose.override.yml # dev-overrides для Docker
├── scripts/
│   └── startapp.sh             # скрипт создания нового приложения
└── src/
    ├── apps/
    │   └── core/               # Custom User, базовые модели
    │       ├── models.py       # User(AbstractUser)
    │       ├── admin.py        # UserAdmin
    │       ├── urls.py         # маршруты приложения
    │       └── views.py        # представления
    ├── config/
    │   ├── settings.py         # настройки проекта
    │   ├── urls.py             # корневые маршруты
    │   ├── wsgi.py
    │   └── asgi.py
    ├── static/                 # статика (CSS, JS, images)
    ├── media/                  # пользовательские файлы
    └── templates/
        ├── base.html           # базовый шаблон
        └── home.html           # стартовая страница
```

---

## Команды Makefile

| Команда              | Описание                           |
|----------------------|------------------------------------|
| `make run`           | Запуск dev-сервера                 |
| `make migrate`       | Создание и применение миграций     |
| `make superuser`     | Создать суперпользователя          |
| `make shell`         | Django shell_plus                  |
| `make sync`          | Установка зависимостей (`uv sync`) |
| `make lock`          | Обновить lockfile (`uv lock`)      |
| `make lint`          | Проверка кода (ruff)               |
| `make format`        | Форматирование кода (ruff)         |
| `make collectstatic` | Сборка статики                     |
| `make docker-up`     | Поднять Docker-контейнеры          |
| `make docker-down`   | Остановить контейнеры              |
| `make docker-logs`   | Логи контейнеров                   |
| `make clean`         | Очистка кэша (__pycache__)         |

> **Без Make?** Все команды можно запускать напрямую. Например:
> `make run` → `uv run python manage.py runserver`

---

## Как создать новое приложение

```bash
./scripts/startapp.sh blog
```

Создаст `src/apps/blog/` с уже настроенным `apps.py` (`name = "apps.blog"`).

После этого:
1. Добавьте `"apps.blog"` в `INSTALLED_APPS` в `src/config/settings.py`
2. Создайте `src/apps/blog/urls.py` и подключите его в `src/config/urls.py`:
   ```python
   path("blog/", include("apps.blog.urls")),
   ```

---

## Ключевые файлы для настройки

| Файл | Что делает |
|---|---|
| `.env` | Секреты и настройки окружения (SECRET_KEY, DEBUG, DATABASE_URL) |
| `src/config/settings.py` | Основные настройки Django |
| `src/config/urls.py` | Корневые URL-маршруты |
| `src/templates/base.html` | Базовый HTML-шаблон (наследуют все страницы) |
| `src/apps/core/models.py` | Кастомная модель User — расширяйте под ваш проект |
| `pyproject.toml` | Зависимости проекта и конфигурация ruff |

---

## FAQ

**Как добавить новую зависимость?**
```bash
uv add django-rest-framework
```

**Как обновить все зависимости?**
```bash
uv lock --upgrade
uv sync
```

**Зачем кастомный User?**
Django [рекомендует](https://docs.djangoproject.com/en/stable/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project) создавать кастомную модель User в начале проекта. Изменить модель User позже — крайне сложно.

**Зачем WhiteNoise?**
Для раздачи статики в production без nginx/CDN. В dev-режиме Django раздаёт статику сам.

**Почему `src/` layout?**
Отделяет исходный код от конфигурационных файлов в корне (`Makefile`, `Dockerfile`, `pyproject.toml`). Это стандартная практика для Python-проектов.
