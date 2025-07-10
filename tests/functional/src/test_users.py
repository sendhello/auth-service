import asyncio

import pytest

from tests.functional.settings import test_settings  # noqa
from tests.functional.utils import get_admin_headers, redis_flush


loop = asyncio.get_event_loop()
pytestmark = pytest.mark.asyncio  # noqa


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
                    "email": "test@test.ru",
                    "role": None,
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
                "email": "test@test.ru",
                "role": None,
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
                "email": "test@test.ru",
                "role": None,
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


@pytest.mark.parametrize(
    "id_, role_id, status_code, result",
    [
        # Ок
        (
            "345fa6c5-c138-4f5c-bce5-a35b0f26fced",
            "0347ef2d-b2e2-4e37-ab6c-130994604317",
            200,
            {
                "first_name": "Тест",
                "id": "345fa6c5-c138-4f5c-bce5-a35b0f26fced",
                "last_name": "Тестов",
                "email": "test@test.ru",
                "role": None,
                "login": None,
            },
        ),
    ],
)
async def test_users_set_role(client, mock_redis, id_, role_id, status_code, result):
    response = client.post(
        f"api/v1/users/{id_}/set_role?role_id={role_id}",
        headers=await get_admin_headers(),
    )
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)


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
                "email": "test@test.ru",
                "role": None,
                "login": None,
            },
        ),
    ],
)
async def test_users_remove_role(client, mock_redis, id_, status_code, result):
    response = client.post(f"api/v1/users/{id_}/remove_role", headers=await get_admin_headers())
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)
