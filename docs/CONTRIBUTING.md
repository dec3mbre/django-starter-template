# Руководство для разработчиков

## Начало работы

```bash
git clone <repo-url> && cd django-starter-template
uv sync                    # установить зависимости
cp .env.example .env       # настроить переменные окружения
make migrate               # создать и применить миграции
make superuser             # создать суперпользователя
make run                   # запустить dev-сервер
```

## Создание нового приложения

### 1. Сгенерировать приложение

```bash
make startapp name=blog
```

Команда создаст `src/apps/blog/` и автоматически пропатчит `apps.py`:

```python
# src/apps/blog/apps.py (после make startapp)
class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.blog"  # ← патчится автоматически
```

### 2. Зарегистрировать в INSTALLED_APPS

```python
# src/config/settings.py
INSTALLED_APPS = [
    ...
    "apps.blog",
]
```

### 3. Подключить URL-маршруты

```python
# src/config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("apps.blog.urls")),
    path("", include("apps.users.urls")),
]
```

### 4. Создать модели, сервисы, URL

Рекомендуемая структура приложения:

```
src/apps/blog/
├── __init__.py
├── apps.py
├── models.py        ← модели (наследуют BaseModel)
├── services.py      ← бизнес-логика (создание, обновление)
├── selectors.py     ← чтение данных (списки, фильтры)
├── views.py         ← HTTP-обработчики
├── urls.py          ← маршруты
├── admin.py         ← регистрация в admin
├── tests.py         ← тесты (или tests/)
└── migrations/
```

### 5. Создать и применить миграции

```bash
make migrate
```

## Структура приложения

### models.py — только данные

Модели описывают структуру и связи. Без бизнес-логики.

```python
from core.models import BaseModel
from django.conf import settings
from django.db import models


class Article(BaseModel):
    title = models.CharField(max_length=200)
    body = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles",
    )
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
```

> Внешние ключи на пользователя — через `settings.AUTH_USER_MODEL`, не через прямой импорт `User`.

### services.py — действия (запись)

Функции с keyword-only аргументами. Содержат бизнес-правила, валидацию, транзакции.

```python
from django.db import transaction
from core.exceptions import ValidationError, PermissionDeniedError
from apps.blog.models import Article


def create_article(*, author, title: str, body: str) -> Article:
    if not title.strip():
        raise ValidationError("Заголовок не может быть пустым")
    return Article.objects.create(author=author, title=title, body=body)


def publish_article(*, article: Article, user) -> Article:
    if article.author != user:
        raise PermissionDeniedError("Только автор может публиковать статью")
    article.is_published = True
    article.save(update_fields=["is_published", "updated_at"])
    return article
```

### selectors.py — запросы (чтение)

Чистые функции, возвращающие `QuerySet` или значения.

```python
from django.db.models import QuerySet
from apps.blog.models import Article


def get_published_articles() -> QuerySet[Article]:
    return Article.objects.filter(is_published=True).select_related("author")


def get_user_articles(*, user) -> QuerySet[Article]:
    return Article.objects.filter(author=user)
```

### views.py — HTTP-слой

Views не содержат бизнес-логику. Их задача: принять запрос → вызвать сервис/селектор → вернуть ответ.

```python
from django.shortcuts import render
from apps.blog.selectors import get_published_articles


def article_list(request):
    articles = get_published_articles()
    return render(request, "blog/article_list.html", {"articles": articles})
```

### admin.py — django-unfold

Все admin-классы наследуют `unfold.admin.ModelAdmin`:

```python
from django.contrib import admin
from unfold.admin import ModelAdmin
from apps.blog.models import Article


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ["title", "author", "is_published", "created_at"]
    list_filter = ["is_published"]
    search_fields = ["title"]
```

## Соглашения по именованию

### Файлы

| Файл | Содержимое |
|---|---|
| `models.py` | Django-модели. Наследуют `BaseModel` (кроме `User`). |
| `services.py` | Функции записи: `create_*`, `update_*`, `delete_*`, `publish_*` |
| `selectors.py` | Функции чтения: `get_*`, `list_*`, `filter_*` |
| `views.py` | HTTP-обработчики |
| `urls.py` | URL-маршруты. Обязательно `app_name`. |
| `admin.py` | Регистрация в admin (unfold.admin.ModelAdmin) |
| `tests.py` | Тесты (или `tests/` при росте) |

### Классы и функции

- Модели — `PascalCase`, единственное число: `Article`, `Order`, `Payment`
- Сервисы — `snake_case`, глагол + существительное: `create_article()`, `cancel_order()`
- Селекторы — `snake_case`, `get_` / `list_` + существительное: `get_published_articles()`
- Views — `snake_case`: `article_list`, `article_detail`
- Admin — `ModelNameAdmin`: `ArticleAdmin`, `OrderAdmin`
- URL names — `snake_case` через `app_name:name`: `blog:article-list`

## Правила импортов

Проект использует `src/`-layout. Импорты пишутся **без** префикса `src.`:

```python
# ✅ Правильно
from core.models import BaseModel
from core.exceptions import ApplicationError, NotFoundError
from apps.users.models import User
from apps.blog.services import create_article

# ❌ Неправильно
from src.core.models import BaseModel
from src.apps.users.models import User
```

Ruff isort настроен с `known-first-party`:

```toml
[tool.ruff.lint.isort]
known-first-party = ["apps", "config", "core"]
```

Порядок импортов (автоматически сортируется `ruff`):

```python
# 1. stdlib
import uuid
from datetime import datetime

# 2. third-party
from django.db import models
from django.conf import settings

# 3. first-party (apps, config, core)
from core.models import BaseModel
from apps.blog.models import Article
```

Внутри приложения используйте **относительные** импорты:

```python
# src/apps/blog/views.py
from .services import create_article
from .selectors import get_published_articles
from .models import Article
```

## Линтер и форматирование

```bash
make lint      # проверить код (ruff check src/)
make format    # отформатировать (ruff format src/ + ruff check --fix src/)
```

Конфигурация в `pyproject.toml`:

- Длина строки: 120 символов
- Target: Python 3.13
- Правила: `E` (pycodestyle), `F` (pyflakes), `I` (isort), `B` (bugbear), `UP` (pyupgrade), `DJ` (django)
- Миграции исключены из проверки

Запускайте `make lint` перед каждым коммитом.

## Управление зависимостями

Проект использует **uv** (не pip):

```bash
# Добавить зависимость
uv add django-filter

# Добавить dev-зависимость
uv add --group dev pytest

# Добавить production-зависимость
uv add --group prod newrelic

# Синхронизировать окружение
uv sync

# Обновить lock-файл
uv lock
```

**Не используйте** `pip install` — все зависимости должны быть в `pyproject.toml`.

## Команды разработки

| Команда | Описание |
|---|---|
| `make run` | Запустить dev-сервер |
| `make shell` | Django shell (`shell_plus`) |
| `make migrate` | `makemigrations` + `migrate` |
| `make superuser` | Создать суперпользователя |
| `make startapp name=X` | Создать приложение в `src/apps/X/` |
| `make lint` | Запустить ruff check |
| `make format` | Автоформатирование ruff |
| `make collectstatic` | Собрать статику |
| `make docker-up` | Запустить Docker (PostgreSQL + Django) |
| `make docker-down` | Остановить Docker |
| `make docker-logs` | Логи Docker |
| `make clean` | Удалить `__pycache__` и `.ruff_cache` |
