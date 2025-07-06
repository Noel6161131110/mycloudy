from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import httpx
from auth.utils import *
import sys, os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

sys.dont_write_bytecode = True

IS_PRODUCTION = os.getenv("ENV_MODE") == "PRODUCTION"

app = FastAPI(
    title="MyCloudy API Gateway",
    version="v1",
    description="API Gateway for MyCloudy Self-hosted Server",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    )

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

services = {
    "auth": f"{os.environ.get('AUTH_SERVICE_URL')}",
    "file": f"{os.environ.get('FILE_SERVICE_URL')}"
}

unprotectedRoutes = {
    "auth": [
        "user/login",
        "user/register"
    ]
}

async def forwardRequest(serviceUrl: str, method: str, path: str, body=None, headers=None):
    async with httpx.AsyncClient() as client:
        url = f"{serviceUrl}{path}"
        response = await client.request(method, url, json=body, headers=headers)
        return response

def isUnprotected(service: str, path: str) -> bool:
    return service in unprotectedRoutes and path in unprotectedRoutes[service]

@app.api_route("/{service}/api/{version}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway(service: str, version: str, path: str, request: Request):
    if service not in services:
        raise HTTPException(status_code=404, detail="Service not found")
    
    serviceUrl = services[service]
    body = await request.json() if request.method in ["POST", "PUT", "PATCH"] else {}
    
    userId = None
    if not isUnprotected(service, path):
        authHeader = request.headers.get("authorization")
        if not authHeader:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        token = authHeader.split(" ")[1] if " " in authHeader else authHeader
        payload = ValidateToken(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        userId = payload.get("userId")
        if not userId:
            raise HTTPException(status_code=401, detail="userId missing in token")
        body["userId"] = userId

    excludedHeaders = {
        "host", "content-length", "connection", "keep-alive", "proxy-authenticate",
        "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"
    }
    forwardHeaders = {k: v for k, v in request.headers.items() if k.lower() not in excludedHeaders}

    try:
        response = await forwardRequest(serviceUrl, request.method, f"/api/{version}/{path}", body, forwardHeaders)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream error: {exc}")
    
    return JSONResponse(status_code=response.status_code, content=response.json())