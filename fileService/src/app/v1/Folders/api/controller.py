from fastapi import File, HTTPException, Depends, Request, Form
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from fastapi.encoders import jsonable_encoder
from src.app.v1.Folders.models.models import Folders, PermissionType
from src.app.v1.FileOperations.models.models import FileModel, Shares
from ..schemas import *
from src.database.db import getSession
from typing import List
from uuid import uuid4, UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from src.security import security
import os
from src.dependencies.auth import getCurrentUserId
from datetime import datetime
from src.app.v1.Activity.models.models import Activity, ActivityType, ActionType, Tags
from src.app.v1.Activity.models.tagModels import FolderTagLink
from sqlalchemy import delete
from sqlalchemy.orm import selectinload
from src.config.variables import STORAGE_DIR

async def deleteFolderDFSStrategy(
    folderId: UUID,
    db: AsyncSession,
    userId: UUID
    ):

    subfolders_result = await db.exec(select(Folders).where(Folders.parentId == folderId))
    subfolders = subfolders_result.all()

    for subfolder in subfolders:
        await deleteFolderDFSStrategy(subfolder.id, db, userId)

  
    filesResult = await db.exec(select(FileModel).where(FileModel.folderId == folderId))
    files = filesResult.all()

    for file in files:

        try:
            if file.filePath and os.path.exists(file.filePath):
                os.remove(file.filePath)
        except Exception as e:
            print(f"Warning: Could not delete file {file.filePath}: {e}")

        # Delete related file activities
        await db.exec(delete(Activity).where(Activity.fileId == file.id))

    await db.exec(delete(Activity).where(Activity.folderId == folderId))

    # Finally delete the folder
    folder_obj = await db.get(Folders, folderId)
    if folder_obj:
        await db.delete(folder_obj)

async def updateParentFoldersUpdatedAt(folder_id: UUID, db: AsyncSession):
    while folder_id:
        folder = await db.get(Folders, folder_id)
        if not folder:
            break
        folder.updatedAt = datetime.now()
        db.add(folder)
        await db.commit()
        await db.refresh(folder)
        folder_id = folder.parentId
class FolderController:
    
    def __init__(self):
        pass
    
    async def getAllFolders(
        self,
        db: AsyncSession = Depends(getSession),
        userId: str = Depends(getCurrentUserId),
    ):
        try:
            result = await db.exec(
                select(Folders)
                .where(Folders.createdBy == userId, Folders.softDeleted == False)
                .options(selectinload(Folders.tags))  # Load tags
            )
            folders = result.all()

            folder_schemas = [FolderGetSchema.model_validate(folder) for folder in folders]

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

            result = await db.exec(
                select(Folders)
                .where(Folders.createdBy == userId, Folders.id == folderId, Folders.softDeleted == False)
                .options(selectinload(Folders.tags))
            )
            
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
            parentId = None
            parentFolder = None
            isVault = False
            
            if folder.parentId:
                parentId = folder.parentId
                parentFolder = await db.get(Folders, parentId)
                
                if not parentFolder:
                    raise HTTPException(status_code=404, detail="Parent folder not found")
                
                if parentFolder.isSystem and parentFolder.name == STORAGE_DIR:
                    isVault = True
            else:
                return JSONResponse(
                    content={"message": "Parent folder is required"},
                    status_code=400
                )

            folder.tagIds = folder.tagIds or []

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

            if folder.tagIds:
                for tagId in folder.tagIds:
                    db.add(FolderTagLink(folderId=newFolder.id, tagId=tagId))

            activity = Activity(
                userId=userId,
                action=ActionType.CREATED,
                entityType=ActivityType.FOLDER,
                folderId=newFolder.id,
                name=newFolder.name,
                parentId=None if isVault else folder.parentId,
                parentFolderName=folder.name if folder.parentId else 'VAULT',
            )

            db.add(activity)

            fileShare = Shares(
                id=uuid4(),
                folderId=newFolder.id,
                sharedWithUserId=userId,
                sharedByUserId=userId,
                permission=PermissionType.OWNER,
                sharedAt=datetime.now()
            )
            
            db.add(fileShare)
            
            await db.commit()
            await db.refresh(newFolder)
            
            await updateParentFoldersUpdatedAt(newFolder.parentId, db)

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
            isVault = False
            
            folder = await db.get(Folders, folderId)

            if not folder or folder.createdBy != userId:
                raise HTTPException(status_code=404, detail="Folder not found")
            
            parent = await db.get(Folders, folder.parentId)

            if parent and parent.isSystem and parent.name == STORAGE_DIR:
                isVault = True

            # Compare and update name
            if folderUpdate.name and folderUpdate.name != folder.name:
                db.add(Activity(
                    userId=userId,
                    action=ActionType.UPDATED,
                    entityType=ActivityType.FOLDER,
                    folderId=folderId,
                    fieldChanged="name",
                    oldValue=folder.name,
                    newValue=folderUpdate.name,
                    parentId=None if isVault else folder.parentId,
                    parentFolderName= parent.name if parent else 'VAULT'
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
        

            if folderUpdate.tagIds:
                
                await db.exec(delete(FolderTagLink).where(FolderTagLink.folderId == folderId))
                
                # Add new tags
                for tag in folderUpdate.tagIds:
                    tag_link = FolderTagLink(folderId=folder.id, tagId=tag)
                    db.add(tag_link)
                    
            await db.commit()
            await db.refresh(folder)
            
            await updateParentFoldersUpdatedAt(folder.parentId, db)

            return folder

        except HTTPException as httpExc:
            raise httpExc

        except Exception as e:
            print(f"Error in updateFolder: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
        
    async def deleteFolder(
        self,
        folderId: UUID,
        userId: UUID = Depends(getCurrentUserId),
        db: AsyncSession = Depends(getSession)
    ):
        try:
            folder = await db.get(Folders, folderId)

            if not folder or folder.createdBy != userId:
                raise HTTPException(status_code=404, detail="Folder not found")

            await deleteFolderDFSStrategy(folderId, db, userId)

            await db.commit()

            return JSONResponse(
                content={"message": "Folder and all its contents deleted successfully"},
                status_code=200
            )

        except HTTPException as httpExc:
            raise httpExc

        except Exception as e:
            print(f"Error in deleteFolder: {e}")
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