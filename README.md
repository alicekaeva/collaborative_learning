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

# Установить зависимости
poetry install --no-root

# Запустить PostgreSQL и Redis через docker compose
docker compose up -d postgres redis

# Настроить .env для локального подключения:
# POSTGRES_SERVER=localhost
# REDIS_URL=redis://:redispassword@localhost:6379/0

# Применить миграции
poetry run alembic upgrade head

# Запустить сервер
poetry run uvicorn app.main:app --reload
```

## Структура проекта

Проект организован как **модульный монолит** — 5 ограниченных контекстов в `app/modules/`,
каждый содержит собственные модели, схемы, репозиторий и роутер.

```
app/
├── modules/
│   ├── identity/       # Пользователи, аутентификация, профили (student/teacher/admin)
│   │   ├── models/     # User, Student, Teacher, Admin
│   │   ├── schemas/    # Pydantic-схемы
│   │   ├── repository.py
│   │   ├── service.py  # AuthService (register/login/refresh/logout)
│   │   └── router.py   # /auth/*, /users/*
│   ├── groups/         # Группы, участники, заявки
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repository.py
│   │   ├── service.py  # GroupService
│   │   └── router.py   # /groups/*
│   ├── content/        # Посты, материалы, цели, задания, встречи
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── crud/
│   │   └── router.py   # /posts/*, /materials/*, /goals/*, /tasks/*, /meetings/*, /learning/*
│   ├── messaging/      # Личные и групповые сообщения
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repository.py
│   │   └── router.py   # /messages/*
│   └── taxonomy/       # Теги и категории
│       ├── models/
│       ├── schemas/
│       ├── repository.py
│       └── router.py   # /categories/*, /tags/*
├── api/
│   └── v1/
│       ├── router.py   # Подключает роутеры всех модулей
│       ├── deps.py     # FastAPI Depends: get_current_user, require_roles, сервисы
│       └── endpoints/  # Тонкие shim-файлы для обратной совместимости
├── db/
│   ├── base.py         # DeclarativeBase, IDMixin
│   ├── associations.py # M2M таблицы
│   └── session.py      # AsyncSession, get_db
├── core/
│   ├── config.py       # Settings (pydantic-settings, из .env)
│   ├── security.py     # JWT, bcrypt
│   ├── exceptions.py   # HTTP-исключения
│   └── limiter.py      # SlowAPI rate limiter
├── services/
│   ├── cache.py        # Redis: кеш рекомендаций + refresh-токены
│   └── storage.py      # Загрузка файлов (MIME-детектирование по magic bytes)
└── main.py             # FastAPI app, lifespan, middleware
alembic/                # Миграции БД
tests/
├── conftest.py         # Фикстуры: client, auth_client, admin_client
├── unit/               # Юнит-тесты (security, storage, ...)
└── integration/        # Интеграционные тесты по модулям (auth, groups, ...)
```

## Аутентификация

Используются JWT Bearer токены (access + refresh). Пример:

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
| POST | `/api/v1/auth/logout` | Выход (отзыв refresh-токена) |
| GET | `/api/v1/auth/me` | Текущий пользователь |
| GET | `/api/v1/posts/` | Список постов (пагинация: skip/limit) |
| GET | `/api/v1/posts/recommended` | Рекомендованные посты (кеш Redis) |
| GET | `/api/v1/groups/` | Список групп |
| POST | `/api/v1/groups/` | Создать группу (ROLE_ADMIN) |
| POST | `/api/v1/groups/{id}/enroll` | Заявка на вступление |
| GET | `/api/v1/learning/groups` | Мои группы |
| GET | `/api/v1/learning/groups/{id}` | Группа с чатом, заданиями, встречами |
| POST | `/api/v1/materials/` | Загрузить материал |
| GET | `/api/v1/messages/dialogs` | Список диалогов |
| GET | `/api/v1/messages/dialog/{user_id}` | История переписки (пагинация) |
| GET | `/api/v1/categories/` | Список категорий |
| GET | `/api/v1/tags/` | Список тегов |

## Docker сервисы

| Сервис | Порт | Описание |
|--------|------|---------|
| API | 8000 | FastAPI приложение |
| PostgreSQL | 5432 | База данных |
| Redis | 6379 | Кеш рекомендаций + хранилище refresh-токенов |
