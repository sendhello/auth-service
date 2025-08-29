from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from starlette import status

from db.postgres import get_session
from models import Membership, Organization, User
from schemas import UserCreate, UserInDB, UserUpdateByAdmin
from schemas.membership import MembershipResponse
from schemas.user import UserResponse
from security import multitenancy_protected

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user(
    user_create: UserCreate, auth_data: tuple[AuthJWT, UserResponse, str] = Depends(multitenancy_protected)
) -> UserResponse:
    """Create a new user. Only admins can create users."""

    authorize, user_claims, current_org = auth_data

    async with get_session(current_org) as session:
        user_data = user_create.model_dump(exclude={"repeat_password", "role"})
        new_user_db = User(**user_data)
        session.add(new_user_db)
        try:
            await session.flush()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User with this phone or email already exists"
            )

        # Create owner membership for the creator
        membership_data = {
            "org_id": current_org,
            "user_id": new_user_db.id,
            "role": user_create.role,
            "is_primary": True,
        }
        new_membership_db = Membership(**membership_data)
        session.add(new_membership_db)
        await session.commit()
        await session.refresh(new_user_db)
        await session.refresh(new_membership_db)

    return UserResponse(
        id=new_user_db.id,
        email=new_user_db.email,
        phone=new_user_db.phone,
        first_name=new_user_db.first_name,
        last_name=new_user_db.last_name,
        login=new_user_db.login,
        status=new_user_db.status,
        memberships=[MembershipResponse.model_validate(new_membership_db, from_attributes=True)],
    )


@router.get("/", response_model=list[UserInDB])
async def get_users(auth_data: tuple[AuthJWT, UserResponse, str] = Depends(multitenancy_protected)) -> list[User]:
    authorize, user_claims, current_org = auth_data

    async with get_session(current_org) as session:
        request = (
            select(Organization).options(joinedload(Organization.memberships)).where(Organization.id == current_org)
        )
        result = await session.execute(request)
        org = result.scalars().first()
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        users = []
        for membership in org.memberships:
            user_db = await User.get_by_id(id_=membership.user_id)
            users.append(UserResponse.model_validate(user_db))

    return users


@router.get("/{id}", response_model=UserInDB)
async def get_user(id: UUID, auth_data: tuple[AuthJWT, UserResponse, str] = Depends(multitenancy_protected)) -> User:
    authorize, user_claims, current_org = auth_data

    async with get_session(current_org) as session:
        request = (
            select(Organization).options(joinedload(Organization.memberships)).where(Organization.id == current_org)
        )
        result = await session.execute(request)
        org = result.scalars().first()
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        availabel_user_ids = [membership.user_id for membership in org.memberships]

    if id not in availabel_user_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found in this organization")

    user = await User.get_by_id(id_=id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exists")

    return user


@router.put("/{id}", response_model=UserInDB)
async def update_user(
    id: UUID,
    user_update: UserUpdateByAdmin,
    auth_data: tuple[AuthJWT, UserResponse, str] = Depends(multitenancy_protected),
) -> User:
    authorize, user_claims, current_org = auth_data

    async with get_session(current_org) as session:
        request = (
            select(Organization).options(joinedload(Organization.memberships)).where(Organization.id == current_org)
        )
        result = await session.execute(request)
        org = result.scalars().first()
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        availabel_user_ids = [membership.user_id for membership in org.memberships]

    if id not in availabel_user_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found in this organization")

    user_db = await User.get_by_id(id_=id)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exists")

    user_dto = user_update.model_dump(exclude_none=True)
    try:
        user_db = await user_db.update(**user_dto)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with such login is registered already",
        )

    return user_db


@router.delete("/{id}", response_model=UserInDB)
async def delete_user(id: UUID, auth_data: tuple[AuthJWT, UserResponse, str] = Depends(multitenancy_protected)) -> User:
    authorize, user_claims, current_org = auth_data

    async with get_session(current_org) as session:
        request = (
            select(Organization).options(joinedload(Organization.memberships)).where(Organization.id == current_org)
        )
        result = await session.execute(request)
        org = result.scalars().first()
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

        availabel_user_ids = [membership.user_id for membership in org.memberships]

    if id not in availabel_user_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not found in this organization")

    user = await User.get_by_id(id_=id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exists")

    return await user.delete()
