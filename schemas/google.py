from pydantic import EmailStr

from .base import Model


class GoogleToken(Model):
    """Токен Google OAuth 2."""

    access_token: str
    refresh_token: str
    expires_in: int
    scope: list[str]
    token_type: str
    id_token: str
    expires_at: float


class UserInfo(Model):
    """Данные сервиса oauth2"""

    id: str
    email: EmailStr | None
    verified_email: bool | None
    name: str | None
    given_name: str | None
    family_name: str | None
    picture: str | None
    locale: str | None
