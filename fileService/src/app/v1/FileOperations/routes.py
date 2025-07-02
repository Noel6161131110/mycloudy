from src.app.v1.FileOperations.api.fileController import *
from fastapi import APIRouter

router = APIRouter()

routes = [
    {
        "method": "POST",
        "name": "Upload File",
        "path": "/upload",
        "endpoint": uploadFile
    },
    {
        "method": "GET",
        "name": "Get Files",
        "path": "/files",
        "endpoint": getFiles
    },
    {
        "method": "GET",
        "name": "Get Video Info",
        "path": "/video/{file_id}",
        "endpoint": getVideoInfo
    },
    {
        "method": "GET",
        "name": "Stream Video",
        "path": "/stream/video/{file_id}",
        "endpoint": streamVideo
    },
    {
        "method": "GET",
        "name": "Stream Audio",
        "path": "/stream/audio/{file_id}",
        "endpoint": streamAudio
    },
    {
        "method": "GET",
        "name": "Show Image",
        "path": "/image/{file_id}",
        "endpoint": showImage
    },
    {
        "method": "PUT",
        "name": "Save Video Time",
        "path": "/video/{file_id}",
        "endpoint": saveVideoTime
    }
]

for route in routes:
    router.add_api_route(route["path"], route["endpoint"], methods=[route["method"]], name=route["name"])