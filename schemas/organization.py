from constants import OrgStatus, Plan

from .base import Model
from .mixins import IdMixin


class OrganizationBase(Model):
    name: str
    slug: str
    plan: Plan = Plan.FREE
    status: OrgStatus = OrgStatus.ACTIVE


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(Model):
    name: str | None = None
    plan: str | None = None
    status: str | None = None


class OrganizationResponse(OrganizationBase, IdMixin):
    """Organization model for API responses"""

    class Config:
        from_attributes = True


class OrganizationInDB(OrganizationResponse):
    """Organization model as stored in database"""

    class Config:
        from_attributes = True
