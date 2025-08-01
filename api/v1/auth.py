from hashlib import md5
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security.http import HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from starlette import status

from core.settings import settings
from db.redis_db import get_redis
from models import History, Membership, User
from schemas import Tokens, UserCreated, UserLogin, UserRegistration, UserResponse
from schemas.membership import MembershipResponse
from security import REFRESH_TOKEN_PROTECTED, TOKEN_PROTECTED


router = APIRouter()


@router.post("/signup", response_model=UserCreated, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserRegistration) -> UserCreated:
    user_dto = jsonable_encoder(user_create)
    try:
        raw_user = await User.create(**user_dto)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with such login is registered already",
        )

    return raw_user


@router.post("/login", response_model=Tokens)
async def login(
    user_login: UserLogin,
    user_agent: str = Header(default=None),
    x_org_id: UUID | None = Header(default=None, alias="X-Org-ID"),
    authorize: AuthJWT = Depends(),
) -> Tokens:
    db_user = await User.get_by_email(email=str(user_login.email))
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not db_user.check_password(user_login.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Load user memberships for multitenancy
    memberships_db = await Membership.get_user_memberships(db_user.id)

    # Create UserResponse with multitenancy data
    user_data = {
        "id": str(db_user.id),
        "email": db_user.email,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "phone": db_user.phone,
        "login": db_user.login,
        "status": db_user.status,
    }

    user = UserResponse.model_validate(user_data)
    user.memberships = [
        MembershipResponse.model_validate(membership, from_attributes=True) for membership in memberships_db
    ]
    tokens = await Tokens.create(
        authorize=authorize,
        user=user,
        user_agent=user_agent,
        org_id=None,
    )

    db_history = History(
        user_id=db_user.id,
        user_agent=user_agent,
    )
    await db_history.save()

    return tokens


@router.post("/logout", dependencies=TOKEN_PROTECTED)
async def logout(
    user_agent: str = Header(default=None),
    authorize: AuthJWT = Depends(),
    redis: Redis = Depends(get_redis),
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
) -> dict:
    access_key = await authorize.get_jwt_subject()
    access_token_expires = settings.authjwt_access_token_expires
    current_access_token = credentials.credentials
    await redis.sadd(access_key, current_access_token)
    await redis.expire(access_key, time=access_token_expires)

    user_claim = await authorize.get_raw_jwt()
    user_agent_hash = md5(user_agent.encode()).hexdigest()
    refresh_key = f"refresh.{user_claim['user_id']}.{user_agent_hash}"
    await redis.delete(refresh_key)
    return {}


@router.post("/refresh", dependencies=REFRESH_TOKEN_PROTECTED)
async def refresh(
    user_agent: str = Header(default=None),
    x_org_id: str = Header(default=None, alias="X-Org-ID"),
    authorize: AuthJWT = Depends(),
    redis: Redis = Depends(get_redis),
):
    old_refresh_key = await authorize.get_jwt_subject()
    await redis.delete(old_refresh_key)

    user_claims = await authorize.get_raw_jwt()

    # Handle organization switching during refresh
    target_org = None
    if x_org_id and x_org_id in user_claims["org_roles"]:
        target_org = x_org_id
    else:
        target_org = user_claims["org"]

    user_db = await User.get_by_id(UUID(user_claims["user_id"]))
    user = UserResponse.model_validate(user_db, from_attributes=True)

    tokens = await Tokens.create(authorize=authorize, user=user, user_agent=user_agent, org_id=target_org)
    return tokens
