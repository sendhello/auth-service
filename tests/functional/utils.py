from hashlib import md5
from uuid import UUID

import orjson
from async_fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder

# Rules import removed - using membership-based system now
from schemas import UserResponse
from tests.functional.redis import redis
from tests.functional.settings import test_settings  # noqa


async def generate_tokens(user: dict, authorize: AuthJWT = AuthJWT(), user_agent: str = "testclient") -> dict:
    user = UserResponse.parse_obj({**user, "id": "345fa6c5-c138-4f5c-bce5-a35b0f26fced"})
    user_claims = orjson.loads(user.json())
    user_agent_hash = md5(user_agent.encode()).hexdigest()

    access_key = f"access.{user.id}.{user_agent_hash}"
    access_token = await authorize.create_access_token(subject=access_key, user_claims=user_claims)

    refresh_key = f"refresh.{user.id}.{user_agent_hash}"
    refresh_token = await authorize.create_refresh_token(subject=refresh_key, user_claims=user_claims)

    await redis.setex(name=refresh_key, time=None, value=refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


async def get_headers(user: dict | None = None):
    header = {"X-Request-Id": "abcdefgh"}
    if user is None:
        return header

    tokens = await generate_tokens(user)
    access_token = tokens["access_token"]
    header.update({"Authorization": f"Bearer {access_token}"})
    return header


async def get_admin_headers():
    admin = UserResponse(
        id=UUID("345fa6c5-c138-4f5c-bce5-a35b0f26fced"),
        email="admin@example.com",
        phone="0123456789",
        first_name="Admin",
        last_name="User",
    )
    tokens = await generate_tokens(jsonable_encoder(admin))
    access_token = tokens["access_token"]
    return {"X-Request-Id": "abcdefgh", "Authorization": f"Bearer {access_token}"}


async def redis_flush(mock_redis):
    redis = await mock_redis()
    await redis.flush()
