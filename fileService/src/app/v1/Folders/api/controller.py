from fastapi import File, HTTPException, Depends, Request, Form
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from fastapi.encoders import jsonable_encoder
from src.app.v1.Folders.models.models import Folders
from ..schemas import *
from src.database.db import getSession
from typing import List
from src.services.grpc_client import validateAccessToken
from uuid import uuid4, UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import HTTPAuthorizationCredentials
from src.security import security
from src.config.variables import FINAL_DIR
import os, ffmpeg, random, string
from src.dependencies.auth import getCurrentUserId
from datetime import datetime
from src.app.v1.Activity.models.models import Activity, ActivityType, ActionType

class FolderController:
    
    def __init__(self):
        pass
    
    async def getAllFolders(
        self,
        db: AsyncSession = Depends(getSession),
        userId: str = Depends(getCurrentUserId),
    ):
        try:
            folders = await db.exec(select(Folders).where(Folders.createdBy == userId))
            result = folders.all()

            folder_schemas: List[FolderGetSchema] = [
                FolderGetSchema.model_validate(folder) for folder in result
            ]

            return JSONResponse(
                content={"result": jsonable_encoder(folder_schemas)},
                status_code=200
            )
        except Exception as e:
            print(f"Error in getAllFolders: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def getFolderById(
        self,
        folderId: UUID,
        userId: str = Depends(getCurrentUserId),
        db: AsyncSession = Depends(getSession)
    ):
        try:

            result = await db.exec(select(Folders).where(Folders.id == folderId, Folders.createdBy == userId))
            folder = result.first()
            
            if not folder:
                raise HTTPException(status_code=404, detail="Folder not found")

            folderSchema = FolderGetSchema.model_validate(folder)

            return JSONResponse(
                content={"result": jsonable_encoder(folderSchema)},
                status_code=200
            )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Error in getFolderById: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
        
    async def createFolder(
        self,
        folder: FolderCreateSchema,
        userId: str = Depends(getCurrentUserId),
        db: AsyncSession = Depends(getSession)
    ):
        try:
            if not folder.parentId:
                result = await db.exec(select(Folders).where(Folders.name == "MYCLOUDY_VAULT", Folders.isSystem == True))
                vaultFolder = result.first()
                if not vaultFolder:
                    raise HTTPException(status_code=404, detail="Vault folder not found")
                folder.parentId = vaultFolder.id

            if not folder.tagId:
                folder.tagId = None

            newFolder = Folders(
                id=uuid4(),
                name=folder.name,
                description=folder.description,
                parentId=folder.parentId,
                createdBy=userId,
                createdAt=datetime.now(),
                updatedAt=datetime.now(),
                isSystem=False
            )

            db.add(newFolder)
            await db.commit()
            await db.refresh(newFolder)

            activity = Activity(
                userId=userId,
                action=ActionType.CREATED,
                entityType=ActivityType.FOLDER,
                folderId=newFolder.id,
                newValue=newFolder.name
            )

            db.add(activity)
            await db.commit()

            return newFolder
        except Exception as e:
            print(f"Error in createFolder: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
        
    async def updateFolder(
        self,
        folderId: UUID,
        folderUpdate: FolderUpdateSchema,
        userId: UUID = Depends(getCurrentUserId),
        db: AsyncSession = Depends(getSession)
    ):
        try:
            folder = await db.get(Folders, folderId)

            if not folder or folder.createdBy != userId:
                raise HTTPException(status_code=404, detail="Folder not found")

            # Compare and update name
            if folderUpdate.name and folderUpdate.name != folder.name:
                db.add(Activity(
                    userId=userId,
                    action=ActionType.UPDATED,
                    entityType=ActivityType.FOLDER,
                    folderId=folderId,
                    fieldChanged="name",
                    oldValue=folder.name,
                    newValue=folderUpdate.name
                ))
                folder.name = folderUpdate.name

            # Compare and update description
            if folderUpdate.description is not None and folderUpdate.description != folder.description:
                db.add(Activity(
                    userId=userId,
                    action=ActionType.UPDATED,
                    entityType=ActivityType.FOLDER,
                    folderId=folderId,
                    fieldChanged="description",
                    oldValue=folder.description or "",
                    newValue=folderUpdate.description or ""
                ))
                folder.description = folderUpdate.description

            folder.updatedAt = datetime.now()
            await db.commit()
            await db.refresh(folder)

            return folder

        except HTTPException as httpExc:
            raise httpExc

        except Exception as e:
            print(f"Error in updateFolder: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")