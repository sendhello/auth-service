from pydantic import EmailStr, Field, field_validator, model_validator

from constants import UserStatus
from schemas.membership import MembershipResponse, MembershipRole
from security.scopes import role_to_scopes

from .base import Model
from .mixins import IdMixin


class BaseUser(Model):
    email: EmailStr


class PersonalUser(Model):
    first_name: str
    last_name: str
    phone: str

    @field_validator("phone", mode="after")
    def validate_phone(cls, value: str) -> str:
        """Validate Australian phone numbers."""

        if not value.startswith("0"):
            raise ValueError("Phone number must start with 0")
        if len(value) < 10 or len(value) > 15:
            raise ValueError("Phone number must be between 10 and 15 characters long")
        return value


class UserLogin(BaseUser):
    password: str


class UserRegistration(UserLogin, PersonalUser):
    pass


class SocialUserCreate(BaseUser, PersonalUser):
    pass


class UserCreate(BaseUser, PersonalUser):
    """Model of user for registration."""

    password: str
    repeat_password: str
    role: MembershipRole = MembershipRole.VIEWER

    @classmethod
    @model_validator(mode="after")
    def validate_passwords(cls, values: dict) -> dict:
        """Validate that password and repeat_password match."""

        if values.get("password") != values.get("repeat_password"):
            raise ValueError("Passwords do not match")

        return values


class UserCreated(BaseUser, PersonalUser, IdMixin):
    """Модель пользователя при выводе после регистрации."""

    pass


class UserResponse(UserCreated):
    """Модель пользователя при авторизации.

    Умеет распаршивать модель UserInDB
    """

    login: str | None = None
    status: UserStatus = UserStatus.ACTIVE
    memberships: list[MembershipResponse] = Field(default_factory=list)

    def to_user_claims(self, current_org_id: str | None = None) -> dict[str, str | list[str]]:
        """Convert UserResponse to UserClaims."""

        org = None
        current_membership = None
        org_roles = {}
        for membership in self.memberships:
            if str(current_org_id) == str(membership.org_id):
                org = membership.org_id
                current_membership = membership

            roles = org_roles.setdefault(str(membership.org_id), [])
            roles.append(membership.role.value)

        return {
            "user_id": str(self.id),
            "login": self.login,
            "email": str(self.email),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "status": self.status.value,
            "org_roles": org_roles,
            "org": org,
            "scopes": " ".join(sorted(role_to_scopes(role=current_membership.role))) if current_membership else "",
        }


class UserInDB(UserResponse):
    """Модель пользователя в БД."""

    pass


class UserUpdate(PersonalUser):
    """Модель пользователя для обновления данных."""

    login: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    current_password: str


class UserUpdateByAdmin(BaseUser, PersonalUser):
    """Model of user for update by admin."""

    email: EmailStr | None = None
    login: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None


class UserChangePassword(Model):
    """Модель пользователя для смены пароля."""

    current_password: str
    new_password: str
