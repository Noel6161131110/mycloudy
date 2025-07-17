from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, BigInteger, ForeignKey, DateTime, String
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Relationship
from src.app.v1.Activity.models.tagModels import FileTagLink, FolderTagLink

if TYPE_CHECKING:
    from src.app.v1.FileOperations.models.models import FileModel
    from src.app.v1.Folders.models.models import Folders
class ActivityType(str, Enum):
    FILE = "FILE"
    FOLDER = "FOLDER"

class ActionType(str, Enum):
    CREATED = "CREATED"
    UPLOADED = "UPLOADED"
    UPDATED = "UPDATED"
    EDITED = "EDITED"
    VIEWED = "VIEWED"
    DELETED = "DELETED"
    SHARED = "SHARED"
    MOVED = "MOVED"
    RENAMED = "RENAMED"
    DOWNLOADED = "DOWNLOADED"

class Activity(SQLModel, table=True):
    __tablename__ = "Activity"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    userId: UUID
    action: ActionType = Field(sa_column=Column("action", String(length=50), nullable=False))
    entityType: ActivityType = Field(sa_column=Column("entityType", String(length=20), nullable=False))
    fileType: Optional[str] = Field(
        default=None, sa_column=Column("fileType", String(length=20), nullable=True)
    )
    name: Optional[str] = Field(
        default=None, sa_column=Column("fileName", Text, nullable=True)
    )

    fileId: Optional[UUID] = Field(default=None, foreign_key="Files.id", ondelete="CASCADE")
    folderId: Optional[UUID] = Field(default=None, foreign_key="Folders.id", ondelete="CASCADE")
    parentId: Optional[UUID] = Field(
        default=None, sa_column=Column("parentId", ForeignKey("Folders.id"), nullable=True)
    )
    
    fieldChanged: Optional[str] = Field(
        default=None, sa_column=Column("fieldChanged", String(length=50))
    )

    oldValue: Optional[str] = Field(default=None, sa_column=Column("oldValue", Text))
    newValue: Optional[str] = Field(default=None, sa_column=Column("newValue", Text))
    
    parentFolderName: Optional[str] = Field(
        default=None, sa_column=Column("parentFolderName", Text, nullable=True)
    )

    timestamp: datetime = Field(
        sa_column=Column("timestamp", DateTime, nullable=False, default=datetime.now())
    )

class RecentlyOpenedFiles(SQLModel, table=True):
    __tablename__ = "RecentlyOpenedFiles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    fileId: UUID = Field(
        sa_column=Column("fileId", ForeignKey("Files.id", ondelete="CASCADE"), nullable=False)
    )
    
    userId: UUID
    
    openedAt: datetime = Field(
        sa_column=Column("openedAt", DateTime, nullable=False, default=datetime.now())
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
    
    files: List["FileModel"] = Relationship(back_populates="tags", link_model=FileTagLink)

    folders: List["Folders"] = Relationship(back_populates="tags", link_model=FolderTagLink)