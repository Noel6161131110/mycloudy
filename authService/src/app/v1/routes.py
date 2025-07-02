from fastapi import APIRouter

from src.app.v1.Users.routes import userRouter as UsersRouter
from src.app.v1.Users.routes import inviteRouter as InviteRouter
from src.app.v1.Users.routes import rolesRouter as RolesRouter
from src.app.v1.Users.routes import authRouter as AuthRouter

router = APIRouter()

router.include_router(UsersRouter, prefix="/users", tags=["Users"])
router.include_router(InviteRouter, prefix="/users/invite", tags=["Invite System"])
router.include_router(RolesRouter, prefix="/users/roles", tags=["Roles"])
router.include_router(AuthRouter, prefix="/users/auth", tags=["Authentication"])