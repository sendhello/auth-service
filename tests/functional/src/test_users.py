import asyncio

import pytest

from tests.functional.settings import test_settings  # noqa
from tests.functional.utils import get_admin_headers, redis_flush

loop = asyncio.get_event_loop()
pytestmark = pytest.mark.asyncio


@pytest.mark.skip("Fix later")
@pytest.mark.parametrize(
    "status_code, result",
    [
        # Ок
        (
            200,
            [
                {
                    "first_name": "Тест",
                    "id": "345fa6c5-c138-4f5c-bce5-a35b0f26fced",
                    "last_name": "Тестов",
                    "phone": "0123456789",
                    "email": "test@test.ru",
                    "login": None,
                }
            ],
        ),
    ],
)
async def test_users_get(client, mock_redis, status_code, result):
    response = client.get("api/v1/users/", headers=await get_admin_headers())
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)


@pytest.mark.skip("Fix later")
@pytest.mark.parametrize(
    "id_, status_code, result",
    [
        # Ок
        (
            "345fa6c5-c138-4f5c-bce5-a35b0f26fced",
            200,
            {
                "first_name": "Тест",
                "id": "345fa6c5-c138-4f5c-bce5-a35b0f26fced",
                "last_name": "Тестов",
                "phone": "0123456789",
                "email": "test@test.ru",
                "login": None,
            },
        ),
    ],
)
async def test_users_get_id(client, mock_redis, id_, status_code, result):
    response = client.get(f"api/v1/users/{id_}", headers=await get_admin_headers())
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)


@pytest.mark.skip("Fix later")
@pytest.mark.parametrize(
    "id_, status_code, result",
    [
        # Ок
        (
            "345fa6c5-c138-4f5c-bce5-a35b0f26fced",
            200,
            {
                "first_name": "Тест",
                "id": "345fa6c5-c138-4f5c-bce5-a35b0f26fced",
                "last_name": "Тестов",
                "phone": "0123456789",
                "email": "test@test.ru",
                "login": None,
            },
        ),
    ],
)
async def test_users_delete(client, mock_redis, id_, status_code, result):
    response = client.delete(f"api/v1/users/{id_}", headers=await get_admin_headers())
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)
