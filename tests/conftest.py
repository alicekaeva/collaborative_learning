"""Общие фикстуры для всех тестов.

Стратегия:
- get_db переопределяется AsyncMock-ом — реальный PostgreSQL не нужен
- get_current_user переопределяется для инъекции готового пользователя в защищённые маршруты
- CRUD и кэш-функции патчатся в каждом тесте через unittest.mock.patch
"""
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_current_user, get_db
from app.core.security import get_password_hash, create_access_token
from app.main import app
from app.models.user import User


# ---------------------------------------------------------------------------
# Фабрики пользователей
# ---------------------------------------------------------------------------

def make_user(
    id: int = 1,
    email: str = "user@example.com",
    full_name: str = "Test User",
    roles: list[str] | None = None,
    points_amount: int = 0,
) -> MagicMock:
    user = MagicMock(spec=User)
    user.id = id
    user.email = email
    user.full_name = full_name
    user.password_hash = get_password_hash("password123")
    user.roles = roles or ["ROLE_USER"]
    user.points_amount = points_amount
    user.phone_number = None
    user.age = None
    user.alma_mater = None
    user.tags = []
    user.student_profile = None
    user.teacher_profile = None
    user.admin_profile = None
    # created_at needs to be serialisable by Pydantic
    from datetime import datetime, timezone
    user.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return user


@pytest.fixture
def regular_user() -> MagicMock:
    return make_user()


@pytest.fixture
def admin_user() -> MagicMock:
    admin_profile = MagicMock()
    admin_profile.user_id = 2
    u = make_user(id=2, email="admin@example.com", roles=["ROLE_USER", "ROLE_ADMIN"])
    u.admin_profile = admin_profile
    return u


# ---------------------------------------------------------------------------
# Мок сессии базы данных
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db() -> AsyncMock:
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    return session


# ---------------------------------------------------------------------------
# HTTP-клиенты
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client(mock_db: AsyncMock) -> AsyncClient:
    """Неаутентифицированный клиент с замоканной БД."""
    async def _override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient, regular_user: MagicMock) -> AsyncClient:
    """Аутентифицированный клиент — обычный пользователь, без реальной проверки токена."""
    app.dependency_overrides[get_current_user] = lambda: regular_user
    token = create_access_token(regular_user.id, regular_user.roles)
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client
    app.dependency_overrides.pop(get_current_user, None)


@pytest_asyncio.fixture
async def admin_client(client: AsyncClient, admin_user: MagicMock) -> AsyncClient:
    """Аутентифицированный клиент — пользователь с ролью ROLE_ADMIN."""
    app.dependency_overrides[get_current_user] = lambda: admin_user
    token = create_access_token(admin_user.id, admin_user.roles)
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client
    app.dependency_overrides.pop(get_current_user, None)
