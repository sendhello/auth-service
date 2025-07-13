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
                    "id": "0347ef2d-b2e2-4e37-ab6c-130994604317",
                    "title": "manager",
                    "rules": ["user_rules"],
                }
            ],
        ),
    ],
)
async def test_roles_get(client, mock_redis, status_code, result):
    response = client.get("api/v1/roles/", headers=await get_admin_headers())
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)


@pytest.mark.parametrize(
    "id_, status_code, result",
    [
        # Ок
        (
            "0347ef2d-b2e2-4e37-ab6c-130994604317",
            200,
            {
                "id": "0347ef2d-b2e2-4e37-ab6c-130994604317",
                "title": "manager",
                "rules": ["user_rules"],
            },
        ),
    ],
)
async def test_roles_get_id(client, mock_redis, id_, status_code, result):
    response = client.get(f"api/v1/roles/{id_}", headers=await get_admin_headers())
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)


@pytest.mark.parametrize(
    "id_, status_code, result",
    [
        # Ок
        (
            "0347ef2d-b2e2-4e37-ab6c-130994604317",
            200,
            {
                "id": "0347ef2d-b2e2-4e37-ab6c-130994604317",
                "title": "manager",
                "rules": ["user_rules"],
            },
        ),
    ],
)
async def test_roles_delete(client, mock_redis, id_, status_code, result):
    response = client.delete(f"api/v1/roles/{id_}", headers=await get_admin_headers())
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)


@pytest.mark.parametrize(
    "id_, rule, status_code, result",
    [
        # Ок
        (
            "0347ef2d-b2e2-4e37-ab6c-130994604317",
            "admin_rules",
            200,
            {
                "id": "0347ef2d-b2e2-4e37-ab6c-130994604317",
                "title": "manager",
                "rules": ["user_rules", "admin_rules"],
            },
        ),
        # Добавление уже существующего права
        (
            "0347ef2d-b2e2-4e37-ab6c-130994604317",
            "user_rules",
            409,
            {"detail": "Role has this rule already"},
        ),
    ],
)
async def test_roles_set_rule(client, mock_redis, id_, rule, status_code, result):
    response = client.post(f"api/v1/roles/{id_}/set_rule?rule={rule}", headers=await get_admin_headers())
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)


@pytest.mark.parametrize(
    "id_, rule, status_code, result",
    [
        # Ок
        (
            "0347ef2d-b2e2-4e37-ab6c-130994604317",
            "user_rules",
            200,
            {
                "id": "0347ef2d-b2e2-4e37-ab6c-130994604317",
                "title": "manager",
                "rules": [],
            },
        ),
        # Попытка убрать несуществующее право
        (
            "0347ef2d-b2e2-4e37-ab6c-130994604317",
            "admin_rules",
            404,
            {"detail": "Role doesn't have this rule"},
        ),
    ],
)
async def test_roles_remove_rule(client, mock_redis, id_, rule, status_code, result):
    response = client.post(f"api/v1/roles/{id_}/remove_rule?rule={rule}", headers=await get_admin_headers())
    assert response.status_code == status_code
    data = response.json()
    assert data == result

    await redis_flush(mock_redis)
