# Django Starter Template
# Шаблон для Django-проектов

Базовый шаблон для быстрого старта новых проектов на Django.

## Особенности
- **Структура**: Исходный код в `src/`
- **Зависимости**: Разделение на `base`, `dev`, `prod`
- **Конфигурация**: `python-decouple` для работы с `.env`
- **Инструменты**:
    - `ruff` (линтер/форматтер)
    - `Makefile` для частых команд
    - `pytest` для тестов

## Быстрый старт

### Требования
- Python 3.10+
- Make (опционально)

### Установка

1. Создать виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Установить зависимости:
   ```bash
   make install
   # или
   pip install -r requirements/dev.txt
   ```

3. Настроить окружение:
   ```bash
   cp .env.example .env
   ```

4. Применить миграции:
   ```bash
   make migrate
   # или
   python manage.py migrate
   ```

5. Запустить сервер:
   ```bash
   make run
   # или
   python manage.py runserver
   ```

## Команды Makefile

- `make run` - Запуск dev-сервера
- `make migrate` - Создание и применение миграций
- `make install` - Установка зависимостей (dev)
- `make test` - Запуск тестов
- `make lint` - Проверка и форматирование кода (ruff)
- `make superuser` - Создание суперпользователя
- `make clean` - Очистка от кэша и временных файлов
