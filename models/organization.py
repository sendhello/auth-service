from typing import Self
from uuid import UUID

from sqlalchemy import Column, Enum, String, select, UniqueConstraint
from sqlalchemy.orm import relationship

from constants import OrgStatus, Plan
from db.postgres import Base, get_session

from .mixins import CRUDMixin, IDMixin


class Organization(Base, IDMixin, CRUDMixin):
    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    plan = Column(Enum(Plan, name="plan", native_enum=True), default=Plan.FREE, nullable=False)
    status = Column(
        Enum(OrgStatus, name="org_status", native_enum=True), index=True, default=OrgStatus.PENDING, nullable=False
    )

    # Relationships
    memberships = relationship("Membership", back_populates="organization", cascade="all, delete-orphan")

    def __init__(
        self, org_id: UUID, name: str, slug: str, plan: Plan = Plan.FREE, status: OrgStatus = OrgStatus.ACTIVE
    ) -> None:
        self.id = org_id
        self.name = name
        self.slug = slug
        self.plan = plan
        self.status = status

    @classmethod
    async def get_by_id(cls, id_: UUID, current_org_id: str) -> Self:
        async with get_session(current_org_id) as session:
            request = select(cls).where(cls.id == id_)
            result = await session.execute(request)
            entity = result.scalars().first()

        return entity

    @classmethod
    async def get_by_slug(
        cls,
        slug: str,
        org_id: UUID,
    ) -> Self:
        async with get_session(org_id) as session:
            request = select(cls).where(cls.slug == slug)
            result = await session.execute(request)
            organization = result.scalars().first()
        return organization

    @classmethod
    async def get_active_organizations(cls, org_id: UUID) -> list[Self]:
        async with get_session(org_id) as session:
            request = select(cls).where(cls.status == "active")
            result = await session.execute(request)
            organizations = result.scalars().all()
        return organizations

    def __repr__(self) -> str:
        return f"<Organization {self.name} ({self.slug})>"
