from uuid import UUID

from constants import MembershipRole

from .base import Model
from .mixins import IdMixin


class MembershipBase(Model):
    role: MembershipRole
    is_primary: bool = False


class MembershipCreate(MembershipBase):
    user_id: UUID


class MembershipUpdate(Model):
    role: MembershipRole | None = None
    is_primary: bool | None = None


class MembershipResponse(MembershipBase, IdMixin):
    """Membership model for API responses"""

    org_id: UUID
    user_id: UUID

    class Config:
        from_attributes = True


class MembershipInDB(MembershipResponse):
    """Membership model as stored in database"""

    class Config:
        from_attributes = True
