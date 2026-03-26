"""Интеграционные тесты для /api/v1/groups/* — создание групп, роли, запись."""
from unittest.mock import AsyncMock, MagicMock, patch



GROUPS_URL = "/api/v1/groups/"


def _make_group(id: int = 1, name: str = "Test Group") -> MagicMock:
    from app.models.group import Group
    group = MagicMock(spec=Group)
    group.id = id
    group.name = name
    group.info = "Test info"
    group.required_teachers = 1
    group.required_students = 5
    group.administrator_id = 2
    group.tags = []
    group.teachers = []
    group.students = []
    return group


# ---------------------------------------------------------------------------
# Исправление эскалации привилегий (CRITICAL): создание группы требует ROLE_ADMIN
# ---------------------------------------------------------------------------

class TestCreateGroup:
    async def test_regular_user_gets_403(self, auth_client):
        """Пользователь только с ROLE_USER должен получить 403."""
        response = await auth_client.post(GROUPS_URL, json={
            "name": "New Group",
            "info": "Some info",
            "required_teachers": 1,
            "required_students": 10,
            "tag_ids": [],
        })
        assert response.status_code == 403

    async def test_admin_can_create_group(self, admin_client, admin_user):
        """Пользователь с ROLE_ADMIN должен успешно создавать группы."""
        group = _make_group(id=1, name="Admin Group")

        with patch("app.api.v1.endpoints.groups.group_crud.create",
                   new_callable=AsyncMock, return_value=group):
            response = await admin_client.post(GROUPS_URL, json={
                "name": "Admin Group",
                "info": "Создана администратором",
                "required_teachers": 1,
                "required_students": 10,
                "tag_ids": [],
            })

        assert response.status_code == 201

    async def test_admin_without_profile_gets_403(self, admin_client, admin_user):
        """ROLE_ADMIN есть, но admin_profile отсутствует — доступ запрещён."""
        admin_user.admin_profile = None  # убираем профиль

        response = await admin_client.post(GROUPS_URL, json={
            "name": "Group",
            "info": "",
            "required_teachers": 1,
            "required_students": 5,
            "tag_ids": [],
        })

        assert response.status_code == 403

    async def test_unauthenticated_gets_401(self, client):
        response = await client.post(GROUPS_URL, json={
            "name": "Group",
            "info": "",
            "required_teachers": 1,
            "required_students": 5,
            "tag_ids": [],
        })
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Список групп — публичный эндпоинт
# ---------------------------------------------------------------------------

class TestListGroups:
    async def test_public_access_returns_200(self, client):
        """Просмотр списка групп не требует токена."""
        with patch("app.api.v1.endpoints.groups.group_crud.get_all",
                   new_callable=AsyncMock, return_value=[]):
            response = await client.get(GROUPS_URL)

        assert response.status_code == 200
        assert response.json() == []

    async def test_returns_group_list(self, client):
        groups = [_make_group(id=i, name=f"Группа {i}") for i in range(1, 4)]
        with patch("app.api.v1.endpoints.groups.group_crud.get_all",
                   new_callable=AsyncMock, return_value=groups), \
             patch("app.api.v1.endpoints.groups.group_crud.get_by_tag",
                   new_callable=AsyncMock), \
             patch("app.api.v1.endpoints.groups.group_crud.get_by_category",
                   new_callable=AsyncMock):
            response = await client.get(GROUPS_URL)

        assert response.status_code == 200
        assert len(response.json()) == 3


# ---------------------------------------------------------------------------
# Мои группы — требует авторизации
# ---------------------------------------------------------------------------

class TestMyGroups:
    async def test_unauthenticated_gets_401(self, client):
        response = await client.get(f"{GROUPS_URL}my")
        assert response.status_code == 401

    async def test_authenticated_returns_200(self, auth_client):
        with patch("app.api.v1.endpoints.groups.group_crud.get_user_groups",
                   new_callable=AsyncMock, return_value=[]):
            response = await auth_client.get(f"{GROUPS_URL}my")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Запись в группу — требует авторизации
# ---------------------------------------------------------------------------

class TestEnroll:
    async def test_unauthenticated_gets_401(self, client):
        response = await client.post(
            f"{GROUPS_URL}1/enroll",
            json={"group_id": 1, "message": "Hi"},
        )
        assert response.status_code == 401

    async def test_nonexistent_group_returns_404(self, auth_client):
        # EnrollRequest требует group_id как в теле, так и в path-параметре
        with patch("app.api.v1.endpoints.groups.group_crud.get_by_id",
                   new_callable=AsyncMock, return_value=None):
            response = await auth_client.post(
                f"{GROUPS_URL}999/enroll",
                json={"group_id": 999, "message": "Хочу вступить"},
            )

        assert response.status_code == 404
