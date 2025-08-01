from typing import Self

from sqlalchemy import Boolean, Column, Enum, ForeignKey, UniqueConstraint, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from constants import MembershipRole
from db.postgres import Base, get_session

from .mixins import CRUDMixin, IDMixin


class Membership(Base, IDMixin, CRUDMixin):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("org_id", "user_id", name="unique_org_user_membership"),)

    org_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), index=True, nullable=False)
    role = Column(Enum(MembershipRole, name="membership_role", native_enum=True), nullable=False)
    is_primary = Column(Boolean, nullable=False, default=False)

    # Relationships
    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User", back_populates="memberships")

    def __init__(self, org_id: UUID, user_id: UUID, role: MembershipRole, is_primary: bool = False) -> None:
        self.org_id = org_id
        self.user_id = user_id
        self.role = role
        self.is_primary = is_primary

    @classmethod
    async def get_user_memberships(cls, user_id: UUID) -> list[Self]:
        """Get all memberships for a user"""
        async with get_session() as session:
            request = select(cls).where(cls.user_id == user_id)
            result = await session.execute(request)
            memberships = result.scalars().all()
        return memberships

    @classmethod
    async def get_org_memberships(cls, org_id: UUID) -> list[Self]:
        """Get all memberships for an organization"""
        async with get_session() as session:
            request = select(cls).where(cls.org_id == org_id)
            result = await session.execute(request)
            memberships = result.scalars().all()
        return memberships

    @classmethod
    async def get_membership(cls, org_id: UUID, user_id: UUID) -> Self:
        """Get specific membership for user in organization"""
        async with get_session() as session:
            request = select(cls).where(cls.org_id == org_id, cls.user_id == user_id)
            result = await session.execute(request)
            membership = result.scalars().first()
        return membership

    @classmethod
    async def get_user_primary_membership(cls, user_id: UUID) -> Self:
        """Get user's primary membership"""
        async with get_session() as session:
            request = select(cls).where(cls.user_id == user_id, cls.is_primary == True)
            result = await session.execute(request)
            membership = result.scalars().first()
        return membership

    def has_role(self, required_role: str) -> bool:
        """Check if membership has required role or higher"""
        role_hierarchy = {
            MembershipRole.VIEWER: 1,
            MembershipRole.COURIER: 2,
            MembershipRole.DISPATCHER: 3,
            MembershipRole.ADMIN: 4,
            MembershipRole.OWNER: 5,
        }

        current_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return current_level >= required_level

    def __repr__(self) -> str:
        return f"<Membership user_id={self.user_id} org_id={self.org_id} role={self.role}>"
