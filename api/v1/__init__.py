from fastapi.routing import APIRouter

from security import ADMIN_REQUIRED, TOKEN_PROTECTED

from .auth import router as auth_router
from .google import router as google_router
from .organizations import router as organizations_router
from .profile import router as profile_router
from .users import router as users_router
from .verify import router as verify_router


router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(google_router, prefix="/google", tags=["Google Auth"])
router.include_router(verify_router, prefix="/verify", tags=["Verify"])
router.include_router(profile_router, prefix="/profile", tags=["Profile"], dependencies=TOKEN_PROTECTED)
router.include_router(users_router, prefix="/users", tags=["Users"], dependencies=ADMIN_REQUIRED)
router.include_router(organizations_router, prefix="/organizations", tags=["Organizations"])
