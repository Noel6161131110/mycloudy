from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column, Text
from sqlalchemy import ForeignKey, DateTime, String
from enum import Enum

class PermissionType(str, Enum):
    VIEWER = "VIEWER"
    OWNER = "OWNER"
    EDITOR = "EDITOR"

class Folders(SQLModel, table=True):
    __tablename__ = "Folders"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str = Field(max_length=100, nullable=False)
    description: Optional[str] = Field(max_length=200, default=None, nullable=True)
    
    folderPath: Optional[str] = Field(
        default=None, sa_column=Column("folderPath", Text, nullable=True)
    )
    
    parentId: Optional[UUID] = Field(
        default=None,
        sa_column=Column("parentId", ForeignKey("Folders.id"), nullable=True)
    )
    
    tagId: Optional[UUID] = Field(
        sa_column=Column(
            "tagId",
            ForeignKey("Tags.id", ondelete="SET NULL"),
            nullable=True
        )
    )
    createdBy: Optional[UUID] = Field(default=None, nullable=True)

    createdAt: Optional[datetime] = Field(
        sa_column=Column("createdAt", DateTime, nullable=False, default=datetime.now())
    )
    updatedAt: Optional[datetime] = Field(
        sa_column=Column("updatedAt", DateTime, nullable=False, default=datetime.now())
    )
    
    isSystem: bool = Field(default=False, nullable=False)
    
    colorHex: Optional[str] = Field(
        default='#808080',
        sa_column=Column("colorHex", String(length=7), nullable=True),
        description="Hex code representing tag color (e.g., #FF5733)"
    )


class Tags(SQLModel, table=True):
    __tablename__ = "Tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=100, nullable=False)
    
    createdBy: Optional[UUID] = Field(default=None, nullable=True)
    description: Optional[str] = Field(max_length=200, default=None, nullable=True)

    createdAt: Optional[datetime] = Field(
        default=None, sa_column=Column("createdAt", DateTime, nullable=False, default=datetime.now())
    )
    
    updatedAt: Optional[datetime] = Field(
        sa_column=Column("updatedAt", DateTime, nullable=False, default=datetime.now())
    )
    
    isSystem: bool = Field(default=False)
    
    colorHex: Optional[str] = Field(
        default='#808080',
        sa_column=Column("colorHex", String(length=7), nullable=True),
        description="Hex code representing tag color (e.g., #FF5733)"
    )


class FolderShares(SQLModel, table=True):
    __tablename__ = "FolderShares"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    folderId: UUID = Field(
        sa_column=Column("folderId", ForeignKey("Folders.id", ondelete="CASCADE"), nullable=False)
    )
    
    sharedWithUserId: UUID
    
    sharedByUserId: UUID
    
    permission: PermissionType = Field(
        sa_column=Column("permission", String(length=20), nullable=False)
    )
    
    sharedAt: datetime = Field(
        sa_column=Column("sharedAt", DateTime, nullable=False, default=datetime.now())
    )