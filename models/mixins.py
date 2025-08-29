import uuid
from datetime import UTC, datetime
from typing import Self

from sqlalchemy import Column, DateTime, select
from sqlalchemy.dialects.postgresql import UUID

from constants import DEFAULT_ORG_ID
from db.postgres import get_session


class CRUDMixin:
    """Mixin-класс предоставляющий частые CRUD операции над моделями."""

    @classmethod
    async def create(cls, commit=True, **kwargs) -> Self:
        instance = cls(**kwargs)
        return await instance.save(commit=commit)

    async def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

        return await self.save(commit=commit)

    async def delete(self, commit=True, current_org: str = DEFAULT_ORG_ID):
        async with get_session(current_org) as session:
            await session.delete(self)
            if commit:
                await session.commit()

        return self

    async def save(self, commit=True, current_org: str = DEFAULT_ORG_ID):
        """Save the current instance to the database.

        In 'current_org' context, it will use the organization ID for multitenancy. Only from token
        """
        async with get_session(current_org) as session:
            session.add(self)
            if commit:
                await session.commit()
                await session.refresh(self)

        return self

    @classmethod
    async def get_all(cls, page: int = 1, page_size: int = 20) -> list[Self]:
        async with get_session() as session:
            request = select(cls).limit(page_size).offset((page - 1) * page_size)
            result = await session.execute(request)
            return result.scalars().all()


class IDMixin:
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    @classmethod
    async def get_by_id(cls, id_: UUID) -> Self:
        async with get_session() as session:
            request = select(cls).where(cls.id == id_)
            result = await session.execute(request)
            return result.scalars().first()
