import os
import sys
from datetime import datetime
from uuid import UUID

from .testdata.data import ROLE_UUID, USER_UUID


sys.path.insert(0, f"{os.getcwd()}/auth_service")

import pytest
from fastapi.testclient import TestClient
from models import History, Role, Rules, User
from models.mixins import CRUDMixin
from tests.functional.redis import redis

from main import app


db = [
    {
        "email": "test@test.ru",
        "password": "password",
        "first_name": "Тест",
        "last_name": "Тестов",
    }
]


@pytest.fixture
def mock_redis():
    async def inner():
        return redis

    return inner


@pytest.fixture
def mock_save():
    async def inner(self: CRUDMixin, commit: bool = True):
        if getattr(self, "id", "") is None:
            self.id = UUID(USER_UUID)
        if getattr(self, "created_at", "") is None:
            self.created_at = datetime(2023, 4, 1)
        if getattr(self, "updated_at", "") is None:
            self.updated_at = datetime(2023, 4, 1)

        return self

    return inner


@pytest.fixture
def mock_user_get_by_email():
    async def inner(email: str):
        user = User(**db[0])
        user.id = UUID(USER_UUID)
        return user

    return inner


@pytest.fixture
def mock_user_get_by_id():
    async def inner(id_: str):
        user = User(**db[0])
        user.id = UUID(USER_UUID)
        return user

    return inner


@pytest.fixture
def mock_get_user():
    async def inner(self, commit=True):
        user = User(**db[0])
        user.id = UUID(USER_UUID)
        return user

    return inner


@pytest.fixture
def mock_user_check_password():
    def inner(self, password: str) -> bool:
        return password == "password"

    return inner


@pytest.fixture
def mock_user_change_password():
    async def inner(self, new_password: str) -> bool:
        user = User(**db[0])
        user.id = UUID(USER_UUID)
        return user

    return inner


@pytest.fixture
def mock_user_get_all():
    async def inner(page, page_size):
        user = User(**db[0])
        user.id = UUID(USER_UUID)
        return [user]

    return inner


@pytest.fixture
def mock_role_get_by_id():
    async def inner(id_: str):
        role = Role(title="manager")
        role.id = UUID(ROLE_UUID)
        role.rules = [Rules.user_rules.value]
        return role

    return inner


@pytest.fixture
def mock_role_get_all():
    async def inner(page, page_size):
        role = Role(title="manager")
        role.id = UUID(ROLE_UUID)
        role.rules = [Rules.user_rules.value]
        return [role]

    return inner


@pytest.fixture
def mock_get_role():
    async def inner(self, commit=True):
        role = Role(title="manager")
        role.id = UUID(ROLE_UUID)
        role.rules = [Rules.user_rules.value]
        return role

    return inner


@pytest.fixture
def mock_history_get_by_user_id():
    async def inner(user_id: UUID, page, page_size):
        history = History(
            user_id=user_id,
            user_agent="testclient",
        )
        history.created_at = datetime(2023, 4, 1)
        return [history]

    return inner


@pytest.fixture
def client(
    monkeypatch,
    mock_redis,
    mock_save,
    mock_user_get_by_email,
    mock_user_get_by_id,
    mock_user_check_password,
    mock_user_change_password,
    mock_user_get_all,
    mock_get_user,
    mock_role_get_by_id,
    mock_role_get_all,
    mock_get_role,
    mock_history_get_by_user_id,
):
    # monkeypatch.setattr('schemas.token.get_redis', mock_redis)
    monkeypatch.setattr("db.redis_db.redis", redis)
    monkeypatch.setattr(CRUDMixin, "save", mock_save)
    monkeypatch.setattr(User, "delete", mock_get_user)
    monkeypatch.setattr(User, "get_by_email", mock_user_get_by_email)
    monkeypatch.setattr(User, "get_by_id", mock_user_get_by_id)
    monkeypatch.setattr(User, "check_password", mock_user_check_password)
    monkeypatch.setattr(User, "change_password", mock_user_change_password)
    monkeypatch.setattr(User, "get_all", mock_user_get_all)
    monkeypatch.setattr(Role, "get_by_id", mock_role_get_by_id)
    monkeypatch.setattr(Role, "get_all", mock_role_get_all)
    monkeypatch.setattr(Role, "delete", mock_get_role)
    monkeypatch.setattr(History, "get_by_user_id", mock_history_get_by_user_id)

    return TestClient(app)
