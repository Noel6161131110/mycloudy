from fastapi import HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from ..models.models import Users, PasswordHash, Roles
from src.database.db import getSession
from src.app.v1.Users.services.auth import GenerateNewAccessToken, ValidateToken, CreateAccessToken, CreateRefreshToken
from src.app.v1.Users.schemas.authSchemas import *
from ..utils import *
from sqlmodel.ext.asyncio.session import AsyncSession


async def LoginUser(user: UsersLoginSchema, db: AsyncSession = Depends(getSession)):
    try:
        userInstance = await db.exec(select(Users).where(Users.email == user.email))
        userInstance = userInstance.first()

        if not userInstance:
            return JSONResponse(content={"message": "User not found"}, status_code=404)
        
        userPassword = await db.exec(select(PasswordHash).where(PasswordHash.userId == userInstance.id))
        userPassword = userPassword.first()

        if not verifyPassword(user.password, userPassword.hash):
            return JSONResponse(content={"message": "Invalid credentials"}, status_code=401)
        
        accessToken = CreateAccessToken(str(userInstance.id))
        refreshToken = CreateRefreshToken(str(userInstance.id))
        
        return JSONResponse(content={"message": "Login successful!",
                                    "accessToken": accessToken,
                                    "refreshToken": refreshToken,
                                    "firstName": userInstance.firstName,
                                    "lastName": userInstance.lastName,
                                    "email": userInstance.email,}, status_code=200)
    except Exception as e:
        print(e)
        return JSONResponse(content={"message": "An error occurred while logging in"}, status_code=500)


async def RefreshAccessToken(
    refreshData: TokenSchema,
    db: AsyncSession = Depends(getSession)
    ) -> JSONResponse:
    try:
        new_token = await GenerateNewAccessToken(refreshData.token, db)
        if not new_token:
            return JSONResponse(content={"message": "Invalid refresh token"}, status_code=401)
        
        return JSONResponse(content={"accessToken": new_token}, status_code=200)
    except Exception as e:
        print(e)
        return JSONResponse(content={"message": "An error occurred while refreshing the access token"}, status_code=500)
    
    
async def ValidateAccessToken(
    accessData: TokenSchema,
    ) -> JSONResponse:
    try:
        payload = await ValidateToken(accessData.token)
        if payload and payload.get('userId'):
            return JSONResponse(content={"message": "Valid token"}, status_code=200)
        else:
            return JSONResponse(content={"message": "Invalid token"}, status_code=401)
    except Exception as e:
        print(e)
        return JSONResponse(content={"message": "An error occurred while validating the token"}, status_code=500)
    
    
