from src.app.v1.Folders.api.controller import *
from fastapi import APIRouter

folderRouter = APIRouter()
tagRouter = APIRouter()

folderController = FolderController()
tagController = TagController()

folderRoutes = [
    {
        "method": "GET",
        "name": "Get Folders",
        "path": "",
        "endpoint": folderController.getAllFolders
    },
    {
        "method": "GET",
        "name": "Get Folder by ID",
        "path": "/{folderId}",
        "endpoint": folderController.getFolderById
    },
    {
        "method": "POST",
        "name": "Create Folder",
        "path": "",
        "endpoint": folderController.createFolder
    },
    {
        "method": "PUT",
        "name": "Update Folder",
        "path": "/{folderId}",
        "endpoint": folderController.updateFolder
    },
    {
        "method": "DELETE",
        "name": "Delete Folder",
        "path": "/perm/{folderId}",
        "endpoint": folderController.deleteFolder
    }
]


tagRoutes = [
    {
        "method": "GET",
        "name": "Get Tags",
        "path": "",
        "endpoint": tagController.getAllTags
    },
    {
        "method": "POST",
        "name": "Create Tag",
        "path": "",
        "endpoint": tagController.createTag
    },
    {
        "method": "PUT",
        "name": "Update Tag",
        "path": "/{tagId}",
        "endpoint": tagController.updateTag
    },
    {
        "method": "DELETE",
        "name": "Delete Tag",
        "path": "/{tagId}",
        "endpoint": tagController.deleteTag
    }
]

for route in folderRoutes:
    folderRouter.add_api_route(route["path"], route["endpoint"], methods=[route["method"]], name=route["name"])

for route in tagRoutes:
    tagRouter.add_api_route(route["path"], route["endpoint"], methods=[route["method"]], name=route["name"])