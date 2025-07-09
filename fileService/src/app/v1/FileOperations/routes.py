from src.app.v1.FileOperations.api.fileController import *
from src.app.v1.FileOperations.api.testfileUpload import *
from fastapi import APIRouter

router = APIRouter()
testRouter = APIRouter()
routes = [
    {
        "method": "POST",
        "name": "Upload File",
        "path": "/upload",
        "endpoint": uploadFile
    },
    {
        "method": "POST",
        "name": "Upload File Chunk",
        "path": "/upload/chunk",
        "endpoint": uploadFileAsChunk
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
    },
    {
        "method": "POST",
        "name": "Test Validate Token",
        "path": "/test/validate-token",
        "endpoint": testValidateToken
    }
]

testRoutes = [
    {
        "method": "POST",
        "name": "Start Upload",
        "path": "/upload/start",
        "endpoint": start_upload
    },
    {
        "method": "POST",
        "name": "Upload Chunk",
        "path": "/upload/chunk",
        "endpoint": upload_chunk
    },
    {
        "method": "POST",
        "name": "Finalize Upload",
        "path": "/upload/finalize",
        "endpoint": finalize_upload
    },
    {
        "method": "GET",
        "name": "Get Upload Status",
        "path": "/upload/status/{file_id}",
        "endpoint": get_upload_status
    }
]

for route in routes:
    router.add_api_route(route["path"], route["endpoint"], methods=[route["method"]], name=route["name"])

for testRoute in testRoutes:
    testRouter.add_api_route(testRoute["path"], testRoute["endpoint"], methods=[testRoute["method"]], name=testRoute["name"])
    
testRouter.add_api_route("/", get_upload_page, methods=["GET"], name="Get Upload Page", response_class=HTMLResponse)