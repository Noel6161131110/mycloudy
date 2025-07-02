from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from ..models.models import Users, InviteLink
from src.database.db import getSession
from src.database.redis import getRedis
from src.app.v1.Users.schemas.inviteSchemas import *
from ..utils import *
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import uuid4
import secrets
from datetime import datetime, timedelta, timezone

async def GenerateInviteLink(
        body: InviteLinkCreateSchema,
        db: AsyncSession = Depends(getSession),
    ):
    try:
        # Validating Phase
        expiryType = str(body.expiryType).upper()
        
        if expiryType not in ["D", "H", "W"]:
            return JSONResponse(content={"message": "Invalid expiry type"}, status_code=400)

        if body.expiryValue <= 0:
            return JSONResponse(content={"message": "Expiry value must be greater than zero"}, status_code=400)

        userInstance = await db.exec(select(Users).where(Users.id == body.userId))
        userInstance = userInstance.first()

        if not userInstance:
            return JSONResponse(content={"message": "User not found"}, status_code=404)
        
        emailExists = await db.exec(select(Users).where(Users.email == body.emailId))
        emailExists = emailExists.first()
        
        if emailExists:
            return JSONResponse(content={"message": "Email already exists"}, status_code=400)
        
        # Creating Invite Link
        
        linkToken = secrets.token_urlsafe(6)[:8]
        
        validTill = None
        dateTimeNow = datetime.now(timezone.utc)

        if expiryType == "D":
            validTill = dateTimeNow + timedelta(days=body.expiryValue)
        elif expiryType == "H":
            validTill = dateTimeNow + timedelta(hours=body.expiryValue)
        elif expiryType == "W":
            validTill = dateTimeNow + timedelta(weeks=body.expiryValue)

        inviteLink = InviteLink(
            id=uuid4(),
            linkToken=linkToken,
            createdBy=body.userId,
            validTill=validTill,
            createdAt=dateTimeNow,
            emailId=body.emailId
        )
        
        db.add(inviteLink)
        await db.commit()
        await db.refresh(inviteLink)
        
        redis = await getRedis()
        redisKey = f"invite:{linkToken}"
        ttl = int((validTill - dateTimeNow).total_seconds())
        await redis.set(redisKey, body.emailId, ex=ttl)

        return JSONResponse(
            content={
                "message": "Invite link created successfully",
                "linkId": inviteLink.linkToken,
                "validTill": validTill.isoformat() if validTill else None
            },
            status_code=201
        )
        
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

async def GetInviteLink(
        userId: UUID = None, 
        db: AsyncSession = Depends(getSession)
    ):
    try:
        if not userId:
            inviteLinks = await db.exec(select(InviteLink))
        else:
            inviteLinks = await db.exec(
                select(InviteLink).where(
                    InviteLink.createdBy == userId
                )
            )
            
        inviteLinks = inviteLinks.all()
        if not inviteLinks:
            return JSONResponse(content={"result": []}, status_code=200)
        
        result = [
            {
                **InviteLinkGetSchema.model_validate(inviteLink).model_dump(mode="json"),
                "validTill": inviteLink.validTill.isoformat() if inviteLink.validTill else None,
                "createdAt": inviteLink.createdAt.isoformat()
            }
            for inviteLink in inviteLinks
        ]
        
        return JSONResponse(content={"result": result}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
    
def GetCreatedUserInfo(inviteId: str, db: Session = Depends(getSession)):
    try:
        inviteLink = db.exec(select(InviteLink).where(InviteLink.linkId == inviteId)).first()
        if not inviteLink:
            return JSONResponse(content={"message": "Invite link not found"}, status_code=404)
        
        userInstance = db.get(Users, inviteLink.userId)
        if not userInstance:
            return JSONResponse(content={"message": "User not found"}, status_code=404)
        
        return JSONResponse(content={"userId": userInstance.id, "email": userInstance.email, "name": userInstance.name}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)
    
