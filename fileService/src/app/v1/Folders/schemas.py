from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class FolderCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    parentId: Optional[UUID] = None # Optional because if None, it means it's a root folder, parentId if given will be uuid
    tagId: Optional[UUID] = None

    class Config:
        from_attributes = True
        

class FolderGetSchema(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    parentId: Optional[UUID] = None
    tagId: Optional[UUID] = None
    createdBy: Optional[UUID] = None
    createdAt: datetime
    updatedAt: datetime
    isSystem: bool

    class Config:
        from_attributes = True

class FolderUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True