from enum import StrEnum


ANONYMOUS = "anonymous"

GOOGLE_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

DEFAULT_ORG_ID = "00000000-0000-0000-0000-000000000000"


class SocialType(StrEnum):
    google = "google"


class UserStatus(StrEnum):
    """Enum-like class for user statuses"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"


class MembershipRole(StrEnum):
    """Enum-like class for membership roles"""

    OWNER = "owner"
    ADMIN = "admin"
    DISPATCHER = "dispatcher"
    COURIER = "courier"
    VIEWER = "viewer"


class Plan(StrEnum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ULTIMATE = "ultimate"


class OrgStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
