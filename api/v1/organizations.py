from uuid import UUID, uuid4

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from starlette import status

from db.postgres import get_session
from models import Membership, MembershipRole, Organization
from schemas import UserResponse
from schemas.membership import (
    MembershipCreate,
    MembershipResponse,
    MembershipUpdate,
)
from schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from security import (
    ADMIN_REQUIRED,
    DISPATCHER_REQUIRED,
    TOKEN_PROTECTED,
    multitenancy_protected,
)

router = APIRouter()


@router.post(
    "/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED, dependencies=TOKEN_PROTECTED
)
async def create_organization(
    org_create: OrganizationCreate,
    authorize: AuthJWT = Depends(),
) -> Organization:
    """Create a new organization.

    Only authenticated users can create organizations.
    """
    user_claims = await authorize.get_raw_jwt()
    new_organisation_uuid = uuid4()

    async with get_session(new_organisation_uuid) as session:
        # Create organization
        org_data = org_create.model_dump()
        new_org = Organization(org_id=new_organisation_uuid, **org_data)
        session.add(new_org)
        try:
            await session.flush()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Organization with this slug already exists"
            )

        # Create owner membership for the creator
        membership_data = {
            "org_id": new_org.id,
            "user_id": user_claims["user_id"],
            "role": MembershipRole.OWNER,
            "is_primary": len(user_claims["org_roles"]) == 0,  # Make primary if user has no other orgs
        }
        new_membership = Membership(**membership_data)
        session.add(new_membership)
        await session.commit()
        await session.refresh(new_org)

    return OrganizationResponse(
        id=new_org.id, name=new_org.name, slug=new_org.slug, plan=new_org.plan, status=new_org.status
    )


@router.get("/", response_model=list[OrganizationResponse], dependencies=TOKEN_PROTECTED)
async def list_organizations(
    auth_data: tuple[AuthJWT, UserResponse, str] = Depends(multitenancy_protected),
) -> list[OrganizationResponse]:
    """List organizations the user has access to."""

    authorize, user_claims, current_org = auth_data

    organizations = []
    for org_id in user_claims["org_roles"]:
        org = await Organization.get_by_id(org_id, org_id)
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        organizations.append(OrganizationResponse.model_validate(org))

    return organizations


@router.get("/{org_id}", response_model=OrganizationResponse, dependencies=TOKEN_PROTECTED)
async def get_organization(
    org_id: UUID, auth_data: tuple[AuthJWT, UserResponse, str] = Depends(multitenancy_protected)
) -> OrganizationResponse:
    """Get organization details."""
    authorize, user_claims, current_org = auth_data

    org = await Organization.get_by_id(org_id, current_org)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return OrganizationResponse.model_validate(org, from_attributes=True)


@router.put("/{org_id}", response_model=OrganizationResponse, dependencies=ADMIN_REQUIRED)
async def update_organization(
    org_id: UUID,
    org_update: OrganizationUpdate,
    auth_data: tuple[AuthJWT, dict, str] = Depends(multitenancy_protected),
) -> OrganizationResponse:
    """Update organization details. Requires admin or owner role."""
    authorize, user_claims, current_org = auth_data

    # Check if user has access to this organization
    if str(org_id) not in user_claims["org_roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this organization")

    org = await Organization.get_by_id(org_id, current_org)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Update organization
    update_data = org_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)

    await org.save(current_org=current_org)
    return OrganizationResponse.model_validate(org, from_attributes=True)


@router.delete("/{org_id}", response_model=OrganizationResponse, dependencies=ADMIN_REQUIRED)
async def delete_organization(
    org_id: UUID, auth_data: tuple[AuthJWT, UserResponse, str] = Depends(multitenancy_protected)
):
    """Delete organization. Only owners can delete organizations."""
    authorize, user_claims, current_org = auth_data

    org = await Organization.get_by_id(org_id, current_org)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    return await org.delete(current_org=current_org)


# Membership management endpoints
@router.post("/{org_id}/memberships", response_model=MembershipResponse, dependencies=ADMIN_REQUIRED)
async def create_membership(
    org_id: UUID,
    membership_create: MembershipCreate,
    auth_data: tuple[AuthJWT, UserResponse, str] = Depends(multitenancy_protected),
) -> MembershipResponse:
    """Add a user to organization. Requires admin or owner role."""

    authorize, user_claims, current_org = auth_data

    # Validate organization exists
    org = await Organization.get_by_id(org_id, current_org)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Create membership
    membership_data = membership_create.model_dump()
    try:
        new_membership = await Membership.create(**membership_data, org_id=org_id)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Membership already exists for this user in this organization",
        )

    return MembershipResponse.model_validate(new_membership, from_attributes=True)


@router.get("/{org_id}/memberships", response_model=list[MembershipResponse], dependencies=DISPATCHER_REQUIRED)
async def list_memberships(
    org_id: UUID, auth_data: tuple[AuthJWT, UserResponse, str] = Depends(multitenancy_protected)
) -> list[MembershipResponse]:
    """List organization memberships. Requires admin or owner role."""
    authorize, user_claims, current_org = auth_data

    memberships = await Membership.get_org_memberships(org_id)
    return [MembershipResponse.model_validate(m, from_attributes=True) for m in memberships]


@router.put("/{org_id}/memberships/{membership_id}", response_model=MembershipResponse, dependencies=ADMIN_REQUIRED)
async def update_membership(
    org_id: UUID,
    membership_id: UUID,
    membership_update: MembershipUpdate,
    auth_data: tuple[AuthJWT, UserResponse, str] = Depends(multitenancy_protected),
) -> MembershipResponse:
    """Update membership. Requires admin or owner role."""
    authorize, user_claims, current_org = auth_data

    membership = await Membership.get_by_id(membership_id)
    if not membership or membership.org_id != org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")

    # Update membership
    update_data = membership_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(membership, field, value)

    await membership.save()
    return MembershipResponse.model_validate(membership, from_attributes=True)


@router.delete(
    "/{org_id}/memberships/{membership_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=ADMIN_REQUIRED
)
async def delete_membership(
    org_id: UUID, membership_id: UUID, auth_data: tuple[AuthJWT, UserResponse, str] = Depends(multitenancy_protected)
):
    """Remove user from organization. Requires admin or owner role."""
    authorize, user_claims, current_org = auth_data

    membership = await Membership.get_by_id(membership_id)
    if not membership or membership.org_id != org_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")

    await membership.delete()
