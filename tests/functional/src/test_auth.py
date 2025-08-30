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
            201,
            {
                "id": "345fa6c5-c138-4f5c-bce5-a35b0f26fced",
                "email": "test@test.ru",
                "phone": "0123456789",
                "first_name": "Тест",
                "last_name": "Тестов",
            },
        ),
    ],
)
async def test_create_user(client, mock_redis, user, status_code, result):
    response = client.post("api/v1/auth/signup", json=user, headers=await get_headers())
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)


@pytest.mark.parametrize(
    "login_data, status_code, result_keys",
    [
        # Ок
        (
            {"email": USER["email"], "password": USER["password"]},
            200,
            ["access_token", "refresh_token"],
        ),
    ],
)
async def test_login(client, mock_redis, login_data, status_code, result_keys):
    response = client.post("api/v1/auth/login", json=login_data, headers=await get_headers())
    assert response.status_code == status_code
    data = response.json()
    assert list(data.keys()) == result_keys

    await redis_flush(mock_redis)
