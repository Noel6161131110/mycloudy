from fastapi import HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from ..models.models import Users, PasswordHash, Roles
from src.database.db import getSession
from src.app.v1.Users.schemas.roleSchemas import *
from ..utils import *
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import uuid4, UUID


async def ChangeUserRole(
        body: UserRoleChangeSchema, 
        db: AsyncSession = Depends(getSession)
    ):
    try:
        userInstance = await db.get(Users, body.userId)
        if not userInstance:
            return JSONResponse(content={"message": "User not found"}, status_code=404)

        roleInstance = await db.get(Roles, body.roleId)
        if not roleInstance:
            return JSONResponse(content={"message": "Role not found"}, status_code=404)

        userInstance.roleId = body.roleId
        db.add(userInstance)
        await db.commit()

        return JSONResponse(content={"message": "User role changed successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def GetRoles(
        db: AsyncSession = Depends(getSession)
    ):
    try:
        roles = await db.exec(select(Roles))
        roles = roles.all()
        
        result = []
        
        for role in roles:
            roleData = RolesGetSchema.model_validate(role).model_dump(mode="json")
            result.append(roleData)
            
        return JSONResponse(content={"roles": result}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))