from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, Header, HTTPException
from starlette import status

from models import History, User
from schemas import UserResponse
from security import TOKEN_PROTECTED, multitenancy_protected


router = APIRouter()


@router.post("/token", response_model=dict, dependencies=TOKEN_PROTECTED)
async def login(
    user_agent: str = Header(default=None), auth_data: tuple[AuthJWT, dict, str] = Depends(multitenancy_protected)
) -> dict:

    authorize, user_claims, current_org = auth_data
    db_user = await User.get_by_id(id_=UUID(user_claims.get("user_id")))
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    db_history = History(
        user_id=db_user.id,
        user_agent=user_agent,
    )
    await db_history.save()

    user = UserResponse.model_validate(db_user, from_attributes=True)
    return user.to_user_claims(current_org)
