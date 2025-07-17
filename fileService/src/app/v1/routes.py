from fastapi import APIRouter
from src.app.v1.FileOperations.routes import router as FileOperationsRouter
from src.app.v1.Folders.routes import folderRouter, tagRouter
from src.app.v1.Activity.routes import ActivityRouter

router = APIRouter()

router.include_router(FileOperationsRouter, prefix="/files", tags=["File Operations"])
router.include_router(folderRouter, prefix="/folders", tags=["Folders"])
router.include_router(tagRouter, prefix="/tags", tags=["Tags"])
router.include_router(ActivityRouter, prefix="/activities", tags=["Activities"])
