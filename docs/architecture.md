# Архитектура проекта

## Структура

```
├── manage.py                  ← точка входа, добавляет src/ в sys.path
├── pyproject.toml             ← зависимости, настройки ruff
├── Makefile                   ← команды разработки
├── Dockerfile                 ← multi-stage сборка
├── docker-compose.yml         ← PostgreSQL 16 + Django
├── docker-compose.override.yml← переопределения для разработки
├── .env / .env.example        ← переменные окружения
│
└── src/                       ← весь Python-код
    ├── config/                ← настройки Django
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    │
    ├── core/                  ← инфраструктура (НЕ Django-приложение)
    │   ├── models.py          ← BaseModel (UUID PK + timestamps)
    │   ├── exceptions.py      ← иерархия исключений
    │   ├── middleware.py       ← RequestLoggingMiddleware
    │   └── utils/             ← общие утилиты
    │
    ├── apps/                  ← Django-приложения
    │   └── users/             ← кастомная модель User
    │       ├── models.py
    │       ├── views.py
    │       ├── urls.py
    │       ├── admin.py
    │       ├── apps.py
    │       └── migrations/
    │
    ├── templates/             ← шаблоны (base.html, home.html)
    ├── static/                ← статика (css/, js/, images/)
    └── media/                 ← загруженные пользователями файлы
```

## Слои

### config/ — конфигурация Django

Стандартный Django-пакет с settings, URL-конфигурацией и entry points (WSGI/ASGI).

Настройки используют **python-decouple** для чтения переменных окружения из `.env`:

```python
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=True, cast=bool)
DATABASES = {
    "default": config(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        cast=db_url,
    )
}
```

### core/ — инфраструктурный пакет

`core/` — **не** Django-приложение. Он не регистрируется в `INSTALLED_APPS`, не имеет `apps.py` и миграций. Это пакет с общей инфраструктурой, которую используют все приложения.

| Модуль | Назначение |
|---|---|
| `core.models` | `BaseModel` — абстрактная модель с UUID PK и timestamps |
| `core.exceptions` | Иерархия бизнес-исключений |
| `core.middleware` | `RequestLoggingMiddleware` |
| `core.utils` | Общие утилиты |

### apps/ — бизнес-логика

Django-приложения с бизнес-логикой. Каждое приложение регистрируется в `INSTALLED_APPS` как `apps.<name>`.

### core/ vs apps/ — что куда

| `core/` (инфраструктура) | `apps/<name>/` (бизнес-логика) |
|---|---|
| Абстрактные модели, исключения | Конкретные модели, views, admin |
| Middleware, утилиты | URL-маршруты, шаблоны |
| Нет миграций, нет AppConfig | Есть `apps.py`, есть в `INSTALLED_APPS` |
| `from core.models import BaseModel` | `from apps.users.models import User` |

## Импорты

`manage.py` добавляет `src/` в `sys.path`:

```python
sys.path.append(str(Path(__file__).resolve().parent / "src"))
```

Это позволяет импортировать модули напрямую:

```python
from core.models import BaseModel
from core.exceptions import ApplicationError
from apps.users.models import User
from config.settings import DEBUG  # редко нужно напрямую
```

Префикс `src.` **никогда** не используется в импортах.

Ruff isort настроен распознавать эти пакеты как first-party:

```toml
# pyproject.toml
[tool.ruff.lint.isort]
known-first-party = ["apps", "config", "core"]
```

## Инфраструктурные компоненты

### BaseModel

Абстрактная модель-основа для всех бизнес-моделей проекта:

```python
# src/core/models.py
import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
```

Все новые модели наследуют `BaseModel`. Исключение — модель `User`, которая наследует `AbstractUser` и использует стандартный `BigAutoField`.

### Исключения

Иерархия бизнес-исключений для сервисного слоя:

```
ApplicationError
├── NotFoundError
├── ValidationError
└── PermissionDeniedError
```

Все исключения поддерживают параметр `extra` для дополнительного контекста:

```python
from core.exceptions import NotFoundError

raise NotFoundError("Статья не найдена", extra={"article_id": article_id})
```

### RequestLoggingMiddleware

Логирует HTTP-запросы с методом, путём, статусом и временем ответа:

```
INFO core.middleware GET /admin/ 200 (12.3ms)
```

Middleware определён в `core.middleware`, но не добавлен в `MIDDLEWARE` по умолчанию. Для активации добавьте в `src/config/settings.py`:

```python
MIDDLEWARE = [
    ...
    "core.middleware.RequestLoggingMiddleware",
]
```

## Модель User

Кастомная модель User создана с первого дня — менять модель пользователя после миграций крайне сложно:

```python
# src/apps/users/models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.get_full_name() or self.username
```

Настройка в `settings.py`:

```python
AUTH_USER_MODEL = "users.User"
```

## Админка

Используется **django-unfold** — все admin-классы наследуют `unfold.admin.ModelAdmin`:

```python
# src/apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
```

## Production-стек

### Docker

Multi-stage сборка: builder компилирует зависимости через `uv`, runtime копирует только `.venv` и исходный код. Приложение работает под непривилегированным пользователем `django`:

```dockerfile
# runtime stage
USER django
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--chdir", "src"]
```

### docker-compose

**Production** (`docker-compose.yml`): PostgreSQL 16 + gunicorn с healthcheck.
**Разработка** (`docker-compose.override.yml`): подменяет gunicorn на `runserver`, монтирует код для hot-reload.

### Статика

**WhiteNoise** раздаёт статику в production без nginx:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    ...
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

### Безопасность

При `DEBUG=False` автоматически включаются:

```python
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Переменные окружения

| Переменная | По умолчанию | Описание |
|---|---|---|
| `SECRET_KEY` | — | **Обязательно**. Секретный ключ Django |
| `DEBUG` | `True` | Режим отладки |
| `ALLOWED_HOSTS` | — | Разрешённые хосты (через запятую) |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | URL базы данных |
| `CSRF_TRUSTED_ORIGINS` | — | Доверенные origins для CSRF (через запятую) |
| `LOG_LEVEL` | `INFO` | Уровень логирования |
| `POSTGRES_DB` | `django_app` | Имя БД для Docker |
| `POSTGRES_USER` | `django` | Пользователь БД для Docker |
| `POSTGRES_PASSWORD` | — | Пароль БД для Docker |

## Dev-инструменты

В режиме `DEBUG=True` автоматически подключаются (если установлены):

- **django-extensions** — `shell_plus`, `show_urls` и другие команды
- **django-debug-toolbar** — панель отладки в браузере
