from fastapi import File, HTTPException, Depends, Request, Form
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from fastapi.encoders import jsonable_encoder
from src.app.v1.Folders.models.models import Folders, Tags
from ..schemas import *
from src.database.db import getSession
from typing import List
from uuid import uuid4, UUID
from sqlmodel.ext.asyncio.session import AsyncSession
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
                colorHex=folder.colorHex or '#808080',
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
            folder.colorHex = folderUpdate.colorHex or '#808080'
            
            await db.commit()
            await db.refresh(folder)

            return folder

        except HTTPException as httpExc:
            raise httpExc

        except Exception as e:
            print(f"Error in updateFolder: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")


class TagController:
    
    def __init__(self):
        pass
    
    async def getAllTags(
        self,
        createdBy: Optional[UUID] = None,
        userId: str = Depends(getCurrentUserId),
        db: AsyncSession = Depends(getSession),
    ):
        try:
            if not createdBy:
                tags = await db.exec(select(Tags))
            else:
                tags = await db.exec(select(Tags).where(Tags.createdBy == createdBy))
            
            result = tags.all()

            tag_schemas: List[TagGetSchema] = [
                TagGetSchema.model_validate(tag) for tag in result
            ]

            return JSONResponse(
                content={"result": jsonable_encoder(tag_schemas)},
                status_code=200
            )
        except Exception as e:
            print(f"Error in getAllTags: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    async def createTag(
        self,
        tag: TagCreateSchema,
        userId: str = Depends(getCurrentUserId),
        db: AsyncSession = Depends(getSession)
    ):
        try:
            newTag = Tags(
                id=uuid4(),
                name=tag.name,
                description=tag.description,
                createdBy=userId,
                createdAt=datetime.now(),
                isSystem=False,
                colorHex=tag.colorHex or '#808080'
            )

            db.add(newTag)
            await db.commit()
            await db.refresh(newTag)

            return JSONResponse(
                content={"result": jsonable_encoder(newTag)},
                status_code=201
            )
        except Exception as e:
            print(f"Error in createTag: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def updateTag(
        self,
        tagId: UUID,
        tagUpdate: TagCreateSchema,
        userId: UUID = Depends(getCurrentUserId),
        db: AsyncSession = Depends(getSession)
    ):
        try:
            tag = await db.get(Tags, tagId)

            if not tag or tag.createdBy != userId:
                raise HTTPException(status_code=404, detail="Tag not found")

            # Compare and update name
            if tagUpdate.name and tagUpdate.name != tag.name:
                tag.name = tagUpdate.name

            # Compare and update description
            if tagUpdate.description is not None and tagUpdate.description != tag.description:
                tag.description = tagUpdate.description

            tag.colorHex = tagUpdate.colorHex or '#808080'
            tag.updatedAt = datetime.now()
            
            await db.commit()
            await db.refresh(tag)

            return JSONResponse(
                content={"result": jsonable_encoder(tag)},
                status_code=200
            )

        except HTTPException as httpExc:
            raise httpExc

        except Exception as e:
            print(f"Error in updateTag: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def deleteTag(
        self,
        tagId: UUID,
        userId: UUID = Depends(getCurrentUserId),
        db: AsyncSession = Depends(getSession)
    ):
        try:
            tag = await db.get(Tags, tagId)

            if not tag or tag.createdBy != userId:
                raise HTTPException(status_code=404, detail="Tag not found")

            await db.delete(tag)
            await db.commit()

            return JSONResponse(
                content={"message": "Tag deleted successfully"},
                status_code=200
            )

        except HTTPException as httpExc:
            raise httpExc

        except Exception as e:
            print(f"Error in deleteTag: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")