"""Интеграционные тесты для /api/v1/users/* — авторизация, профили, начисление баллов."""
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import AsyncClient

from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.main import app
from tests.conftest import make_user


USERS_URL = "/api/v1/users/"


@pytest_asyncio.fixture
async def teacher_client(client: AsyncClient) -> AsyncClient:
    """Клиент с ролью ROLE_TEACHER — нужен для эндпоинта earn-points."""
    teacher = make_user(id=10, email="teacher@example.com", roles=["ROLE_USER", "ROLE_TEACHER"])
    app.dependency_overrides[get_current_user] = lambda: teacher
    token = create_access_token(teacher.id, teacher.roles)
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client
    app.dependency_overrides.pop(get_current_user, None)


# ---------------------------------------------------------------------------
# Требование авторизации (исправление CRITICAL: закрыт анонимный доступ)
# ---------------------------------------------------------------------------

class TestUsersRequireAuth:
    async def test_list_without_auth_returns_401(self, client):
        """GET /users/ должен отклонять неаутентифицированные запросы."""
        response = await client.get(USERS_URL)
        assert response.status_code == 401

    async def test_get_without_auth_returns_401(self, client):
        """GET /users/{id} должен отклонять неаутентифицированные запросы."""
        response = await client.get(f"{USERS_URL}1")
        assert response.status_code == 401

    async def test_update_without_auth_returns_401(self, client):
        response = await client.patch(f"{USERS_URL}1", json={"full_name": "New"})
        assert response.status_code == 401

    async def test_delete_without_auth_returns_401(self, client):
        response = await client.delete(f"{USERS_URL}1")
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Аутентифицированный доступ
# ---------------------------------------------------------------------------

class TestListUsers:
    async def test_authenticated_returns_200(self, auth_client, regular_user):
        with patch("app.api.v1.endpoints.users.user_crud.get_all",
                   new_callable=AsyncMock, return_value=[regular_user]):
            response = await auth_client.get(USERS_URL)

        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list)
        assert body[0]["email"] == regular_user.email

    async def test_empty_list_returns_200(self, auth_client):
        with patch("app.api.v1.endpoints.users.user_crud.get_all",
                   new_callable=AsyncMock, return_value=[]):
            response = await auth_client.get(USERS_URL)

        assert response.status_code == 200
        assert response.json() == []


class TestGetUser:
    async def test_existing_user_returns_200(self, auth_client, regular_user):
        with patch("app.api.v1.endpoints.users.user_crud.get_by_id",
                   new_callable=AsyncMock, return_value=regular_user):
            response = await auth_client.get(f"{USERS_URL}{regular_user.id}")

        assert response.status_code == 200
        assert response.json()["id"] == regular_user.id

    async def test_nonexistent_user_returns_404(self, auth_client):
        with patch("app.api.v1.endpoints.users.user_crud.get_by_id",
                   new_callable=AsyncMock, return_value=None):
            response = await auth_client.get(f"{USERS_URL}9999")

        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Обновление профиля — только владелец или администратор
# ---------------------------------------------------------------------------

class TestUpdateUser:
    async def test_user_can_update_own_profile(self, auth_client, regular_user):
        updated = make_user(id=regular_user.id, email="updated@example.com", full_name="Updated")
        with patch("app.api.v1.endpoints.users.user_crud.get_by_id",
                   new_callable=AsyncMock, return_value=regular_user), \
             patch("app.api.v1.endpoints.users.user_crud.update_user",
                   new_callable=AsyncMock, return_value=updated):
            response = await auth_client.patch(
                f"{USERS_URL}{regular_user.id}",
                json={"full_name": "Updated"},
            )

        assert response.status_code == 200

    async def test_user_cannot_update_other_profile(self, auth_client, regular_user):
        other_id = regular_user.id + 1
        response = await auth_client.patch(
            f"{USERS_URL}{other_id}",
            json={"full_name": "Hacked"},
        )
        assert response.status_code == 403

    async def test_admin_can_update_any_profile(self, admin_client, regular_user):
        updated = make_user(id=regular_user.id, full_name="Admin-updated")
        with patch("app.api.v1.endpoints.users.user_crud.get_by_id",
                   new_callable=AsyncMock, return_value=regular_user), \
             patch("app.api.v1.endpoints.users.user_crud.update_user",
                   new_callable=AsyncMock, return_value=updated):
            response = await admin_client.patch(
                f"{USERS_URL}{regular_user.id}",
                json={"full_name": "Admin-updated"},
            )

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Начисление баллов — только для преподавателей, с проверкой границ
# ---------------------------------------------------------------------------

class TestEarnPoints:
    # FastAPI выполняет require_roles("ROLE_TEACHER") ДО валидации тела запроса,
    # поэтому обычный пользователь всегда получает 403, а не 422.
    # Валидация схемы (422) покрыта юнит-тестами в tests/unit/test_schemas.py.

    async def test_regular_user_cannot_earn_points(self, auth_client):
        """Пользователь с ролью ROLE_USER получает 403."""
        response = await auth_client.post(
            f"{USERS_URL}1/points",
            json={"points": 10},
        )
        assert response.status_code == 403

    async def test_negative_points_rejected_for_teacher(self, teacher_client):
        """Преподаватель с отрицательными баллами получает 422 от Pydantic."""
        response = await teacher_client.post(
            f"{USERS_URL}1/points",
            json={"points": -10},
        )
        assert response.status_code == 422

    async def test_zero_points_rejected_for_teacher(self, teacher_client):
        response = await teacher_client.post(
            f"{USERS_URL}1/points",
            json={"points": 0},
        )
        assert response.status_code == 422

    async def test_oversized_points_rejected_for_teacher(self, teacher_client):
        response = await teacher_client.post(
            f"{USERS_URL}1/points",
            json={"points": 99999},
        )
        assert response.status_code == 422
