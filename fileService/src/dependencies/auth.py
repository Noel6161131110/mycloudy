from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from src.security import security
from src.services.grpc_client import validateAccessToken
from uuid import UUID

async def getCurrentUserId(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Authorization token missing"
        )

    accessToken = credentials.credentials
    result = await validateAccessToken(accessToken)

    if result.get("status") != "valid":
        raise HTTPException(status_code=401, detail="Invalid access token")

    return UUID(result["userId"])