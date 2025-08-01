from typing import Self

from sqlalchemy import Column, Enum, ForeignKey, String, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import joinedload, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from constants import UserStatus
from db.postgres import Base, get_session

from .membership import Membership
from .mixins import CRUDMixin, IDMixin


class User(Base, IDMixin, CRUDMixin):
    __tablename__ = "users"

    login = Column(String(255), unique=True)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(255), unique=True, nullable=False)
    password = Column(String(255))
    first_name = Column(String(50))
    last_name = Column(String(50))
    status = Column(Enum(UserStatus, name="user_status", native_enum=True), default=UserStatus.ACTIVE, nullable=False)

    # relationships
    memberships = relationship("Membership", back_populates="user", cascade="all, delete-orphan")
    socials = relationship("Social", back_populates="user", passive_deletes=True)
    history = relationship("History", back_populates="user", passive_deletes=True)

    def __init__(
        self,
        phone: str,
        email: str,
        first_name: str,
        last_name: str,
        password: str = None,
    ) -> None:
        self.phone = phone
        self.email = email
        self.password = generate_password_hash(password) if password is not None else None
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    async def change_password(self, password: str, commit: bool = True) -> bool:
        self.password = generate_password_hash(password)
        return await self.save(commit=commit)

    @classmethod
    async def get_by_login(cls, username: str) -> Self:
        async with get_session() as session:
            request = select(cls).where(cls.login == username)
            result = await session.execute(request)
            user = result.scalars().unique().first()

        return user

    @classmethod
    async def get_by_email(cls, email: str) -> Self:
        async with get_session() as session:
            request = select(cls).options(joinedload(cls.memberships)).where(cls.email == email)
            result = await session.execute(request)
            user = result.scalars().unique().first()

        return user

    @classmethod
    async def get_all(cls, page: int = 1, page_size: int = 20) -> list[Self]:
        async with get_session() as session:
            request = select(cls).options(joinedload(cls.memberships)).limit(page_size).offset((page - 1) * page_size)
            result = await session.execute(request)
            users = result.scalars().unique().all()

        return users

    @classmethod
    async def get_by_id(cls, id_: UUID, without_memberships: bool = False) -> Self:
        async with get_session() as session:
            request = select(cls)
            if not without_memberships:
                request = request.options(joinedload(cls.memberships))

            request = request.where(cls.id == id_)
            result = await session.execute(request)
            users = result.scalars().unique().first()

        return users

    async def get_memberships(self) -> list:
        """Get all memberships for this user"""

        return await Membership.get_user_memberships(self.id)

    async def get_primary_membership(self):
        """Get primary membership for this user"""

        return await Membership.get_user_primary_membership(self.id)

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Social(Base, IDMixin, CRUDMixin):
    __tablename__ = "socials"

    social_id = Column(String(255), nullable=False, unique=True)
    type = Column(String(255), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="socials")

    @classmethod
    async def get_by_social_id(cls, social_id: str) -> Self:
        async with get_session() as session:
            request = select(cls).where(cls.social_id == social_id)
            result = await session.execute(request)
            entity = result.scalars().first()

        return entity
