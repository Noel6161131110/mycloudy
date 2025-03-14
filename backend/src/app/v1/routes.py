from fastapi import APIRouter
from src.app.v1.FileOperations.routes import router as FileOperationsRouter
from src.app.v1.Users.routes import router as UsersRouter

router = APIRouter()

router.include_router(FileOperationsRouter, prefix="/file-operations", tags=["File Operations"])
router.include_router(UsersRouter, prefix="/users", tags=["Users"])