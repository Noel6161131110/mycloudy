import jwt
from datetime import datetime, timedelta, timezone
from ..models.models import *
from jose import JWTError
from src.config.variables import SECRET_KEY
from fastapi import HTTPException, Depends
from src.database.db import getSession
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

async def GetUserById(
    userId: UUID, 
    db: AsyncSession = Depends(getSession)
    ):
    try:
        result = await db.exec(select(Users).where(Users.id == userId))
        user = result.first()
        if not user:
            return None
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def CreateAccessToken(userId: str):
    try:
        payload = {
            'userId': userId,
            'exp': datetime.now(timezone.utc) + timedelta(days=1)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    except Exception as e:
        print(e)
        return None

def CreateRefreshToken(userId: str):
    try:
        payload = {
            'userId': userId,
            'exp': datetime.now(timezone.utc) + timedelta(days=90)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    except Exception as e:
        print(e)
        return None
    
    
async def ValidateToken(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print(payload)
        return payload
    except JWTError as e:
        print(e)

        if "expired" in str(e).lower():
            print("Token has expired.")
        elif "signature" in str(e).lower():
            print("Invalid signature.")
        else:
            print(f"JWT Error: {e}")
        return None
    
async def ValidateAccessToken(token, db: AsyncSession):
    try:
        payload = await ValidateToken(token)
        if payload and payload.get('userId'):
            userExist = await GetUserById(payload.get('userId'), db=db)
            if userExist:
                return userExist
            else:
                return None
    except Exception as e:
        print(f"Error in ValidateAccessToken: {e}")
    return None



async def GenerateNewAccessToken(refresh_token: str, db: Session):
    
    try:
        payload = await ValidateToken(refresh_token)
        print(payload)
        if payload and payload.get('userId'):
            userExist = await GetUserById(userId=payload.get('userId'), db=db)
            if userExist:
                print(userExist)
                return CreateAccessToken(str(payload.get('userId')))
    except Exception as e:
        print(f"Error in GenerateNewAccessToken: {e}")
    return None

def GenerateTokens(user_id: int):
    try:
        access_token = CreateAccessToken(user_id)
        refresh_token = CreateRefreshToken(user_id)
        return access_token, refresh_token
    except Exception as e:
        print(f"Error in GenerateTokens: {e}")
    return None, None

