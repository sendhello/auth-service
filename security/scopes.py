from enum import StrEnum


class UserRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    DISPATCHER = "dispatcher"
    COURIER = "courier"
    VIEWER = "viewer"


class BaseServiceScopes:
    service = NotImplemented

    @property
    def read(self) -> str:
        return f"{self.service}:read"

    @property
    def write(self) -> str:
        return f"{self.service}:write"

    @property
    def delete(self) -> str:
        return f"{self.service}:delete"

    @property
    def read_self(self) -> str:
        return f"{self.service}:read_self"

    @property
    def write_self(self) -> str:
        return f"{self.service}:write_self"

    @property
    def full_access(self) -> list[str]:
        return [self.read, self.write, self.read_self, self.write_self]


class ProfileScopes(BaseServiceScopes):
    service = "profile"


class UsersScopes(BaseServiceScopes):
    service = "users"


class OrganisationsScopes(BaseServiceScopes):
    service = "organisations"


class RoutesScopes(BaseServiceScopes):
    service = "routes"


class CouriersScopes(BaseServiceScopes):
    service = "couriers"


class MediaScopes(BaseServiceScopes):
    service = "media"


def role_to_scopes(role: str) -> list[str]:
    """Map roles to scopes/permissions"""

    profile_scopes = ProfileScopes()
    users_scopes = UsersScopes()
    organisations_scopes = OrganisationsScopes()
    routes_scopes = RoutesScopes()
    couriers_scopes = CouriersScopes()
    media_scopes = MediaScopes()

    role_scopes = {
        UserRole.OWNER: [
            *profile_scopes.full_access,
            *users_scopes.full_access,
            *organisations_scopes.full_access,
            *routes_scopes.full_access,
            *couriers_scopes.full_access,
            *media_scopes.full_access,
        ],
        UserRole.ADMIN: [
            *profile_scopes.full_access,
            *users_scopes.full_access,
            *organisations_scopes.full_access,
            *routes_scopes.full_access,
            *couriers_scopes.full_access,
            *media_scopes.full_access,
        ],
        UserRole.DISPATCHER: [
            *profile_scopes.write_self,
            *users_scopes.full_access,
            *organisations_scopes.read_self,
            *routes_scopes.full_access,
            *couriers_scopes.full_access,
            media_scopes.read,
            media_scopes.write_self,
        ],
        UserRole.COURIER: [
            *profile_scopes.write_self,
            *organisations_scopes.read_self,
            routes_scopes.write_self,
            routes_scopes.read_self,
            couriers_scopes.write_self,
            couriers_scopes.read_self,
            media_scopes.read_self,
            media_scopes.write_self,
        ],
        UserRole.VIEWER: [profile_scopes.read_self],
    }
    return role_scopes.get(UserRole(role), [])
