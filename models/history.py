from typing import Self

from sqlalchemy import Column, ForeignKey, String, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db.postgres import Base, get_session

from .mixins import CRUDMixin, IDMixin


class History(Base, IDMixin, CRUDMixin):
    __tablename__ = "history"

    user_agent = Column(String(255), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="history")

    def __init__(self, user_id: UUID, user_agent: str) -> None:
        self.user_id = user_id
        self.user_agent = user_agent

    @classmethod
    async def get_by_user_id(cls, user_id: UUID, page: int = 1, page_size: int = 20) -> list[Self]:
        async with get_session() as session:
            request = select(cls).where(cls.user_id == user_id).limit(page_size).offset((page - 1) * page_size)
            result = await session.execute(request)
            return result.scalars().all()

    def __repr__(self) -> str:
        return f"<History element {self.user_agent}>"
