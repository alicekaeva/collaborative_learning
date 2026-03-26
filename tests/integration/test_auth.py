"""Интеграционные тесты для /api/v1/auth/* — регистрация, вход, выход, токены."""
from unittest.mock import AsyncMock, patch

from tests.conftest import make_user


REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
LOGOUT_URL = "/api/v1/auth/logout"
REFRESH_URL = "/api/v1/auth/refresh"
ME_URL = "/api/v1/auth/me"


# ---------------------------------------------------------------------------
# Регистрация
# ---------------------------------------------------------------------------

class TestRegister:
    async def test_success_returns_token_pair(self, client):
        new_user = make_user(id=1, email="new@example.com")

        with patch("app.api.v1.endpoints.auth.user_crud.get_by_email", return_value=None), \
             patch("app.api.v1.endpoints.auth.user_crud.create", return_value=new_user), \
             patch("app.api.v1.endpoints.auth.store_refresh_token", new_callable=AsyncMock):
            response = await client.post(REGISTER_URL, json={
                "email": "new@example.com",
                "password": "securepass",
                "full_name": "New User",
            })

        assert response.status_code == 201
        body = response.json()
        assert "access_token" in body
        assert "refresh_token" in body

    async def test_duplicate_email_returns_409(self, client):
        existing = make_user(email="taken@example.com")

        with patch("app.api.v1.endpoints.auth.user_crud.get_by_email", return_value=existing):
            response = await client.post(REGISTER_URL, json={
                "email": "taken@example.com",
                "password": "pass",
                "full_name": "Someone",
            })

        assert response.status_code == 409

    async def test_invalid_email_returns_422(self, client):
        response = await client.post(REGISTER_URL, json={
            "email": "not-an-email",
            "password": "pass",
            "full_name": "User",
        })
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Вход
# ---------------------------------------------------------------------------

class TestLogin:
    async def test_valid_credentials_returns_token_pair(self, client):
        from app.core.security import get_password_hash
        user = make_user(email="alice@example.com")
        user.password_hash = get_password_hash("correctpassword")

        with patch("app.api.v1.endpoints.auth.user_crud.get_by_email", return_value=user), \
             patch("app.api.v1.endpoints.auth.user_crud.authenticate", return_value=True), \
             patch("app.api.v1.endpoints.auth.store_refresh_token", new_callable=AsyncMock):
            response = await client.post(LOGIN_URL, json={
                "email": "alice@example.com",
                "password": "correctpassword",
            })

        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert "refresh_token" in body

    async def test_wrong_password_returns_401(self, client):
        user = make_user(email="alice@example.com")

        with patch("app.api.v1.endpoints.auth.user_crud.get_by_email", return_value=user), \
             patch("app.api.v1.endpoints.auth.user_crud.authenticate", return_value=False):
            response = await client.post(LOGIN_URL, json={
                "email": "alice@example.com",
                "password": "wrong",
            })

        assert response.status_code == 401

    async def test_unknown_email_returns_401(self, client):
        with patch("app.api.v1.endpoints.auth.user_crud.get_by_email", return_value=None):
            response = await client.post(LOGIN_URL, json={
                "email": "nobody@example.com",
                "password": "pass",
            })
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Выход — проверка владельца токена (исправление CRITICAL-уязвимости)
# ---------------------------------------------------------------------------

class TestLogout:
    async def test_own_token_succeeds(self, auth_client, regular_user):
        with patch("app.api.v1.endpoints.auth.validate_refresh_token",
                   new_callable=AsyncMock, return_value=regular_user.id), \
             patch("app.api.v1.endpoints.auth.revoke_refresh_token",
                   new_callable=AsyncMock):
            response = await auth_client.post(LOGOUT_URL, json={"refresh_token": "valid-token"})

        assert response.status_code == 200

    async def test_other_users_token_returns_403(self, auth_client, regular_user):
        """Пользователь не может отозвать refresh-токен, принадлежащий другому."""
        other_user_id = regular_user.id + 999

        with patch("app.api.v1.endpoints.auth.validate_refresh_token",
                   new_callable=AsyncMock, return_value=other_user_id):
            response = await auth_client.post(LOGOUT_URL, json={"refresh_token": "stolen-token"})

        assert response.status_code == 403

    async def test_without_auth_returns_401(self, client):
        response = await client.post(LOGOUT_URL, json={"refresh_token": "some-token"})
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# /me
# ---------------------------------------------------------------------------

class TestMe:
    async def test_returns_current_user(self, auth_client, regular_user):
        response = await auth_client.get(ME_URL)
        assert response.status_code == 200
        body = response.json()
        assert body["email"] == regular_user.email
        assert body["id"] == regular_user.id

    async def test_without_auth_returns_401(self, client):
        response = await client.get(ME_URL)
        assert response.status_code == 401
