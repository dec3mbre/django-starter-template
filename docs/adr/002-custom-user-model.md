# ADR-002: Кастомная модель User с первого дня

**Статус:** принято  
**Дата:** 2025-01-01

## Контекст

Django предоставляет встроенную модель `django.contrib.auth.models.User`. Она работает «из коробки», но имеет жёсткую структуру: `username`, `email`, `first_name`, `last_name`.

Официальная документация Django [настоятельно рекомендует](https://docs.djangoproject.com/en/stable/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-new-project) создавать кастомную модель пользователя **в начале проекта**. Менять `AUTH_USER_MODEL` после первой миграции — крайне сложная операция, требующая пересоздания всей базы данных.

## Решение

Создана модель `User`, наследующая `AbstractUser`:

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

Регистрация в настройках:

```python
# src/config/settings.py
AUTH_USER_MODEL = "users.User"
```

Модель `User` **не** наследует `BaseModel` — она использует стандартный `BigAutoField` как первичный ключ и собственные timestamp-поля Django (`date_joined`, `last_login`).

## Альтернативы

### Использовать стандартный `django.contrib.auth.models.User`

**Плюсы:** ноль настройки.  
**Минусы:** невозможно добавить поля (email как логин, аватар, роль) без создания связанной модели `Profile`. Миграция на кастомную модель позже — огромная боль.

### Наследовать `AbstractBaseUser`

**Плюсы:** полный контроль над полями (можно убрать `username`, сделать `email` основным).  
**Минусы:** нужно самостоятельно реализовать менеджер, формы, admin. Избыточно для стартового шаблона.

## Последствия

**Положительные:**
- Любые поля (`phone`, `avatar`, `role`) добавляются напрямую в модель через обычную миграцию.
- `AbstractUser` сохраняет всю стандартную функциональность: `username`, `email`, `is_staff`, `groups`, `permissions`.
- Admin работает через стандартный `UserAdmin` (с адаптацией под django-unfold).
- Все внешние ключи (`ForeignKey(settings.AUTH_USER_MODEL)`) указывают на правильную модель.

**Отрицательные:**
- Приложение `users` обязательно с самого начала, даже если кастомных полей ещё нет.
- Начальная миграция должна быть создана до `migrate` — иначе Django создаст таблицы для встроенного `User`.
