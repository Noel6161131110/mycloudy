from src.app.v1.Folders.api.controller import *
from fastapi import APIRouter

folderRouter = APIRouter()
tagRouter = APIRouter()
FolderController = FolderController()

folderRoutes = [
    {
        "method": "GET",
        "name": "Get Folders",
        "path": "",
        "endpoint": FolderController.getAllFolders
    },
    {
        "method": "GET",
        "name": "Get Folder by ID",
        "path": "/{folderId}",
        "endpoint": FolderController.getFolderById
    },
    {
        "method": "POST",
        "name": "Create Folder",
        "path": "",
        "endpoint": FolderController.createFolder
    },
    {
        "method": "PUT",
        "name": "Update Folder",
        "path": "/{folderId}",
        "endpoint": FolderController.updateFolder
    }
]


tagRoutes = [

]

for route in folderRoutes:
    folderRouter.add_api_route(route["path"], route["endpoint"], methods=[route["method"]], name=route["name"])

for route in tagRoutes:
    tagRouter.add_api_route(route["path"], route["endpoint"], methods=[route["method"]], name=route["name"])