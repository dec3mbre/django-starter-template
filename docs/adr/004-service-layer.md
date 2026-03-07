# ADR-004: Сервисный слой — бизнес-логика вне views.py

**Статус:** принято  
**Дата:** 2025-01-01

## Контекст

В стандартном Django бизнес-логика часто попадает во views или модели:

- **Fat views** — views содержат валидацию, запросы к БД, отправку email. Логику невозможно переиспользовать между view и management-командой.
- **Fat models** — модели обрастают методами, знают о смежных доменах. Возникают циклические импорты.

Оба подхода ломаются при росте проекта: тесты становятся хрупкими, логику сложно найти, дублирование растёт.

## Решение

Бизнес-логика размещается в отдельных модулях внутри каждого приложения:

```
src/apps/orders/
├── models.py       ← чистые модели, только поля и Meta
├── services.py     ← действия (create, update, cancel)
├── selectors.py    ← чтение данных (списки, фильтры)
├── views.py        ← HTTP-слой: валидация ввода → вызов сервиса → ответ
├── admin.py
├── urls.py
└── tests/
    ├── test_services.py
    └── test_selectors.py
```

### Разделение ответственности

| Слой | Файл | Отвечает за | Примеры |
|---|---|---|---|
| **Модели** | `models.py` | Структура данных, связи, Meta | Поля, `__str__`, `ordering` |
| **Сервисы** | `services.py` | Запись, мутации, бизнес-правила | `create_order()`, `cancel_order()` |
| **Селекторы** | `selectors.py` | Чтение, фильтрация, агрегация | `get_user_orders()`, `get_order_stats()` |
| **Views** | `views.py` | HTTP: парсинг запроса → ответ | Вызов сервисов и селекторов |

### Пример сервиса

```python
# src/apps/orders/services.py
from django.db import transaction
from core.exceptions import ValidationError
from apps.orders.models import Order


def create_order(*, user, items: list[dict]) -> Order:
    """Создать заказ. Вся бизнес-логика здесь."""
    if not items:
        raise ValidationError("Заказ не может быть пустым", extra={"user_id": user.pk})

    with transaction.atomic():
        order = Order.objects.create(user=user)
        order.add_items(items)
    return order
```

### Пример селектора

```python
# src/apps/orders/selectors.py
from django.db.models import QuerySet
from apps.orders.models import Order


def get_user_orders(*, user, status: str | None = None) -> QuerySet[Order]:
    """Получить заказы пользователя с опциональной фильтрацией."""
    qs = Order.objects.filter(user=user)
    if status:
        qs = qs.filter(status=status)
    return qs.select_related("user")
```

### Пример view

```python
# src/apps/orders/views.py
from django.http import JsonResponse
from apps.orders.services import create_order
from apps.orders.selectors import get_user_orders


def order_list(request):
    orders = get_user_orders(user=request.user)
    return JsonResponse({"orders": list(orders.values("id", "status"))})
```

### Правила

1. **views.py** не обращается к `Model.objects` напрямую — только через сервисы и селекторы.
2. **services.py** — функции с keyword-only аргументами (`*` в сигнатуре). Возвращают объекты моделей.
3. **selectors.py** — чистые функции чтения. Возвращают `QuerySet` или значения.
4. **models.py** — поля, `Meta`, `__str__`. Без бизнес-логики. Допустимы property для вычисляемых атрибутов.
5. Исключения из `core.exceptions` используются для бизнес-ошибок.

## Альтернативы

### Fat Views (стандартный Django)

**Плюсы:** просто, всё в одном месте, минимум файлов.  
**Минусы:** логика привязана к HTTP, не переиспользуется в management-командах, Celery-задачах, тестах.

### Fat Models (Active Record)

**Плюсы:** логика рядом с данными, вызов через `order.cancel()`.  
**Минусы:** модели обрастают зависимостями, циклические импорты, сложно тестировать изолированно.

### Django Service Objects (библиотека)

**Плюсы:** формализованный паттерн с классами.  
**Минусы:** лишняя зависимость, функции проще классов для большинства случаев.

## Последствия

**Положительные:**
- Бизнес-логику можно вызвать из view, management-команды, Celery-задачи, теста — без дублирования.
- Тесты сервисов не требуют HTTP — быстрее и надёжнее.
- Чёткая точка входа для code review: вся логика в `services.py`.
- Селекторы можно оптимизировать независимо (`select_related`, `prefetch_related`, кеширование).

**Отрицательные:**
- Больше файлов в приложении.
- Для простых CRUD-операций может выглядеть как over-engineering.
- Нужна дисциплина команды — соблазн «быстро написать в views» остаётся.
