import asyncio

import pytest

from tests.functional.settings import test_settings  # noqa
from tests.functional.testdata.data import USER
from tests.functional.utils import get_headers, redis_flush

loop = asyncio.get_event_loop()
pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "user, status_code, result",
    [
        # Ок
        (
            USER,
            200,
            {
                "first_name": "Тест",
                "id": "345fa6c5-c138-4f5c-bce5-a35b0f26fced",
                "last_name": "Тестов",
                "email": "test@test.ru",
                "phone": "0123456789",
                "login": None,
                "status": "active",
                "type": "access",
                "memberships": [],
            },
        ),
    ],
)
async def test_profile(client, mock_redis, user, status_code, result):
    response = client.get("api/v1/profile/", headers=await get_headers(user))
    assert response.status_code == status_code
    data = response.json()
    data = {k: v for k, v in data.items() if k not in {"exp", "jti", "nbf", "sub", "fresh", "iat"}}
    assert data == result

    await redis_flush(mock_redis)


@pytest.mark.skip("Fix later")
@pytest.mark.parametrize(
    "user, status_code, result",
    [
        # Ок
        (
            USER,
            200,
            [
                {"created_at": "2023-04-01T00:00:00", "user_agent": "testclient"},
            ],
        ),
    ],
)
async def test_profile_history(client, mock_redis, user, status_code, result):
    response = client.get("api/v1/profile/history", headers=await get_headers(user))
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)


@pytest.mark.skip("Fix later")
@pytest.mark.parametrize(
    "user, status_code, result",
    [
        # Ок
        (
            {
                "email": USER["email"],
                "first_name": USER["first_name"],
                "last_name": "Брокенов",
                "current_password": USER["password"],
            },
            200,
            {
                "id": "345fa6c5-c138-4f5c-bce5-a35b0f26fced",
                "email": "test@test.ru",
                "first_name": "Тест",
                "last_name": "Брокенов",
                "role": None,
                "rules": None,
                "login": None,
            },
        ),
    ],
)
async def test_profile_update(client, mock_redis, user, status_code, result):
    response = client.post("api/v1/profile/update", headers=await get_headers(user), json=user)
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)


@pytest.mark.skip("Fix later")
@pytest.mark.parametrize(
    "user, change_password, status_code, result",
    [
        # Ок
        (
            USER,
            {
                "current_password": USER["password"],
                "new_password": "123qwe",
            },
            200,
            {
                "id": "345fa6c5-c138-4f5c-bce5-a35b0f26fced",
                "email": "test@test.ru",
                "first_name": "Тест",
                "last_name": "Тестов",
                "role": None,
                "rules": None,
                "login": None,
            },
        ),
    ],
)
async def test_profile_change_password(client, mock_redis, user, change_password, status_code, result):
    response = client.post(
        "api/v1/profile/change_password",
        headers=await get_headers(user),
        json=change_password,
    )
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)
