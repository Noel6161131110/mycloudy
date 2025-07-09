from fastapi import APIRouter
from src.app.v1.FileOperations.routes import router as FileOperationsRouter, testRouter

router = APIRouter()

router.include_router(FileOperationsRouter, prefix="/file-operations", tags=["File Operations"])
router.include_router(testRouter, prefix="/test-file-operations", tags=["Test File Operations"])