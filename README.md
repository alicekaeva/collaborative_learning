# Система для совместного обучения — REST API

FastAPI + PostgreSQL + Redis + SQLAlchemy 2.0 (async) + Alembic

## Быстрый старт

```shell
git clone https://github.com/alicekaeva/collaborative_learning
cd collaborative_learning

# Скопировать и настроить переменные окружения
cp .env.example .env
# Отредактировать .env при необходимости

# Запустить через Docker Compose
docker compose up -d --build
```

API будет доступен по адресу: **http://localhost:8000**

### Загрузка тестовых данных (опционально)

После запуска контейнеров можно загрузить seed-данные из оригинального дампа (9 пользователей, группы, посты, сообщения и т.д.):

```shell
docker compose exec -T postgres psql -U cluser -d collaborative_learning -f /init/seed.sql
# или через Make:
make seed
```

Все пользователи из дампа имеют пароль: **`password123`**

Примеры аккаунтов для входа:

| Email | Роль |
|-------|------|
| `alice@example.com` | Admin, Teacher |
| `bob@example.com` | Teacher |
| `charlie@example.com` | Student |

Интерактивная документация:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Локальная разработка (без Docker)

Требуется Python 3.12 или 3.13 (3.14 не поддерживается зависимостями).

```shell
# Установить Poetry (если ещё не установлен)
pip install poetry==1.8.4

# Установить зависимости и создать виртуальное окружение
poetry install

# Активировать окружение
poetry shell

# Запустить PostgreSQL и Redis (например через docker compose)
docker compose up -d postgres redis

# Настроить .env для локального подключения:
# POSTGRES_SERVER=localhost
# REDIS_URL=redis://:redispassword@localhost:6379/0

# Применить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload
```

## Структура проекта

```
app/
├── api/v1/endpoints/   # Эндпоинты FastAPI
├── core/               # Конфиг, безопасность, исключения
├── crud/               # Операции с БД
├── db/                 # Сессия SQLAlchemy
├── models/             # ORM модели
├── schemas/            # Pydantic схемы
├── services/           # Redis кеш, файловое хранилище
└── main.py             # Точка входа
alembic/                # Миграции БД
```

## Аутентификация

Используются JWT Bearer токены. Пример использования:

```shell
# Регистрация
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123","full_name":"Иван Иванов"}'

# Логин
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'

# Запрос с токеном
curl http://localhost:8000/api/v1/posts/ \
  -H "Authorization: Bearer <access_token>"
```

## Роли

| Роль | Описание |
|------|---------|
| `ROLE_USER` | Базовая роль для всех |
| `ROLE_STUDENT` | Студент (участник групп) |
| `ROLE_TEACHER` | Преподаватель (создаёт задания, встречи, цели) |
| `ROLE_ADMIN` | Администратор (управление группами и пользователями) |

## Основные эндпоинты

| Метод | Путь | Описание |
|-------|------|---------|
| POST | `/api/v1/auth/register` | Регистрация |
| POST | `/api/v1/auth/login` | Вход |
| POST | `/api/v1/auth/refresh` | Обновление токена |
| GET | `/api/v1/posts/` | Список постов |
| GET | `/api/v1/posts/recommended` | Рекомендованные посты |
| GET | `/api/v1/groups/` | Список групп |
| POST | `/api/v1/groups/` | Создать группу |
| GET | `/api/v1/learning/groups` | Мои группы |
| GET | `/api/v1/learning/groups/{id}` | Группа с чатом, заданиями, встречами |
| POST | `/api/v1/materials/` | Загрузить материал |
| GET | `/api/v1/messages/dialogs` | Список диалогов |

## Docker сервисы

| Сервис | Порт | Описание |
|--------|------|---------|
| API | 8000 | FastAPI приложение |
| PostgreSQL | 5432 | База данных |
| Redis | 6379 | Кеш и хранилище токенов |
