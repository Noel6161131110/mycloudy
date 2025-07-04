from fastapi import HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from ..models.models import Users, PasswordHash, Roles, InviteLink
from src.database.db import getSession
from src.database.redis import getRedis
from src.app.v1.Users.services.auth import CreateAccessToken, CreateRefreshToken
from src.app.v1.Users.schemas.userSchemas import *
from ..utils import *
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timedelta, timezone
from uuid import uuid4, UUID


async def GetUsers(
        db: AsyncSession = Depends(getSession)
    ):
    try:
        stmt = select(Users, Roles).join(Roles, Users.roleId == Roles.id)
        result = await db.exec(stmt)
        rows = result.all()

        users = []
        for user, role in rows:
            userData = UsersGetSchema.model_validate(user).model_dump(mode="json")
            userData["role"] = role.name if role else None

            users.append(userData)

        return JSONResponse(content={"users": users}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def CreateOnboardingUser(
        user: UserCreateSchema, 
        db: AsyncSession = Depends(getSession), 
        status: str = "onboarding"
    ):
    try:
        emailValid = CheckEmailFormat(user.email)
        if not emailValid:
            return JSONResponse(content={"message": "Invalid email format"}, status_code=400)

        users = await db.exec(select(Users).where(Users.email == user.email))
        users = users.first()
      
        if users:
            return JSONResponse(content={"message": "User already exists"}, status_code=400)

        result = await db.exec(select(Users).limit(1))
        users = result.first()

        if not users and status == "onboarding":

            result = await db.exec(select(Roles).where(Roles.name == "admin"))
            userRole = result.first()
            if not userRole:
                return JSONResponse(content={"message": "Admin role not found"}, status_code=500)
            
            newUser = Users(id=uuid4(), roleId=userRole.id, **user.dict())
            db.add(newUser)
            await db.flush()
            
            # Hashing the password including salt
            
            salt, hashedPassword = hashPassword(user.password)
            
            userPassword = PasswordHash(
                id=uuid4(),
                userId=newUser.id,
                hash=hashedPassword,
                salt=salt
            )
            
            db.add(userPassword)

            await db.commit()
            await db.refresh(newUser)

            # Generating access and refresh tokens
            
            accessToken = CreateAccessToken(str(newUser.id))
            refreshToken = CreateRefreshToken(str(newUser.id))
            
            return JSONResponse(
                content={   
                        "message": "User created successfully!",
                        "accessToken": accessToken,
                        "refreshToken": refreshToken,
                        "firstName": newUser.firstName,
                        "lastName": newUser.lastName,
                        "email": newUser.email,
                },
                status_code=201
            )

        else:
            return JSONResponse(content={"message": "Not an onboarding user"}, status_code=400)
            
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    

async def UpdateUser(
    user: UserUpdateSchema = Body(...), 
    db: AsyncSession = Depends(getSession)):
    try:
        userInstance = await db.get(Users, user.id)
        if not userInstance:
            return JSONResponse(status_code=404, content={"message": "User not found"})

        # Update fields
        for key, value in user.dict(exclude={"id"}, exclude_unset=True).items():
            setattr(userInstance, key, value)

        await db.commit()
        await db.refresh(userInstance)

        return JSONResponse(content={"message": "User updated successfully!"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def UpdatePassword(
        body: PasswordUpdateSchema, 
        db: AsyncSession = Depends(getSession)
    ):
    try:
        userInstance = await db.get(Users, body.id)
        if not userInstance:
            return JSONResponse(status_code=404, content={"message": "User not found"})

        # Hash the new password

        salt, hashedPassword = hashPassword(body.password)
        userPassword = await db.exec(select(PasswordHash).where(PasswordHash.userId == userInstance.id))
        userPassword = userPassword.first()
        
        if not userPassword:
            userPassword = PasswordHash(
                id=uuid4(),
                userId=userInstance.id,
                hash=hashedPassword,
                salt=salt
            )
            db.add(userPassword)
        else:
            userPassword.hash = hashedPassword
            userPassword.salt = salt
        
        await db.commit()
        await db.refresh(userInstance)

        return JSONResponse(content={"message": "Password updated successfully!"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

async def DeleteUser(
        body: UserIdSchema, 
        db: AsyncSession = Depends(getSession)
    ):
    try:
        userInstance = await db.get(Users, body.id)
        if not userInstance:
            raise HTTPException(status_code=404, detail="User not found")

        await db.delete(userInstance)
        await db.commit()

        return JSONResponse(content={"message": "User deleted successfully!"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def CreateInviteUser(
        body: InviteUserCreateSchema, 
        db: AsyncSession = Depends(getSession)
    ):

    try:
        
        redis = await getRedis()
        linkKey = f"invite:{body.linkToken}"
        
        email = await redis.get(linkKey)
        
        inviteLink = None
        if not email:
            result = await db.exec(select(InviteLink).where(InviteLink.linkToken == body.linkToken))
            inviteLink = result.first()

            if not inviteLink:
                return JSONResponse(content={"message": "Invalid invite link"}, status_code=400)
            
            now = datetime.now(timezone.utc)
            if inviteLink.validTill < now:
        
                await db.delete(inviteLink)
                await db.commit()
                return JSONResponse(content={"message": "Token expired"}, status_code=410)
            
            email = inviteLink.emailId
            
            ttl_seconds = int((inviteLink.validTill - now).total_seconds())
            await redis.set(linkKey, email, ex=ttl_seconds)

        result = await db.exec(select(Users).where(Users.email == email))
  
        if result.first():
            return JSONResponse(content={"message": "Email already exists"}, status_code=400)
        
        
        roleInstance = await db.exec(select(Roles).where(Roles.name == 'member'))
        roleInstance = roleInstance.first()

        newUser = Users(
            id=uuid4(),
            firstName=body.firstName,
            lastName=body.lastName,
            email=email,
            roleId=roleInstance.id if roleInstance else None,
        )
        db.add(newUser)
        await db.flush()

        salt, hashedPassword = hashPassword(body.password)
        userPassword = PasswordHash(
            id=uuid4(),
            userId=newUser.id,
            hash=hashedPassword,
            salt=salt
        )
        db.add(userPassword)

        await db.commit()
        await db.refresh(newUser)
        
        if inviteLink:
            await db.delete(inviteLink)
        else:
            
            inviteLink = await db.exec(select(InviteLink).where(InviteLink.linkToken == body.linkToken))
            inviteLink = inviteLink.first()
            if inviteLink:
                await db.delete(inviteLink)
                await db.commit()
                
        await redis.delete(linkKey)
        await db.commit()

        accessToken = CreateAccessToken(str(newUser.id))
        refreshToken = CreateRefreshToken(str(newUser.id))

        return JSONResponse(
            content={
                "message": "User created successfully!",
                "accessToken": accessToken,
                "refreshToken": refreshToken,
                "firstName": newUser.firstName,
                "lastName": newUser.lastName,
                "email": newUser.email,
            },
            status_code=201
        )

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))