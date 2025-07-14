from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class FolderCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    parentId: Optional[UUID] = None # Optional because if None, it means it's a root folder, parentId if given will be uuid
    tagId: Optional[UUID] = None
    colorHex: Optional[str] = Field(
        default=None,
        pattern=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
        description="Hex color code, e.g., #FFF or #ffffff"
    )
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
    colorHex: Optional[str] = Field(
        default=None,
        pattern=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
        description="Hex color code, e.g., #FFF or #ffffff"
    )
    
    class Config:
        from_attributes = True

class TagGetSchema(BaseModel):
    id: UUID
    name: str
    createdBy: Optional[UUID] = None
    description: Optional[str] = None
    createdAt: datetime
    isSystem: bool
    colorHex: Optional[str] = Field(
        default=None,
        pattern=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
        description="Hex color code, e.g., #FFF or #ffffff"
    )

    class Config:
        from_attributes = True

class TagCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    colorHex: Optional[str] = Field(
        default=None,
        pattern=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
        description="Hex color code, e.g., #FFF or #ffffff"
    )
    class Config:
        from_attributes = True