from fastapi import APIRouter
from src.app.v1.FileOperations.routes import router as FileOperationsRouter

router = APIRouter()

router.include_router(FileOperationsRouter, prefix="/files", tags=["File Operations"])
