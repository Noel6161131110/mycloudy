from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import Text, BigInteger, ForeignKey, DateTime, Float, String, Boolean
from enum import Enum
from src.app.v1.Activity.models.tagModels import FileTagLink

if TYPE_CHECKING:
    from src.app.v1.Activity.models.models import Tags
class PermissionType(str, Enum):
    VIEWER = "VIEWER"
    OWNER = "OWNER"
    EDITOR = "EDITOR"
    

class FileModel(SQLModel, table=True):
    __tablename__ = "Files"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    title: str = Field(max_length=50)
    description: str = Field(max_length=200)

    fileName: str = Field(sa_column=Column("fileName", Text, nullable=False))
    fileExtension: str = Field(sa_column=Column("fileExtension", String(length=10), nullable=False))
    fileSize: int = Field(sa_column=Column("fileSize", BigInteger, nullable=False))
    filePath: str = Field(sa_column=Column("filePath", Text, nullable=False))
    fileType: str = Field(sa_column=Column("fileType", String(length=20), nullable=False))

    lastModified: datetime = Field(
        sa_column=Column("lastModified", DateTime, nullable=False)
    )
    folderId: UUID = Field(
        sa_column=Column(
            "folderId",
            ForeignKey("Folders.id", ondelete="CASCADE"),
            nullable=False
        )
    )
    

    totalVideoLength: Optional[float] = Field(
        sa_column=Column("totalVideoLength", Float, nullable=False, default=None)
    )
    
    tags: List["Tags"] = Relationship(back_populates="files", link_model=FileTagLink)
    
    softDeleted: bool = Field(default=False, nullable=False)
    
    
class VideoStreamInfo(SQLModel, table=True):
    __tablename__ = "VideoStreamInfo"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    fileId: UUID = Field(
        sa_column=Column("fileId", ForeignKey("Files.id", ondelete="CASCADE"), nullable=False)
    )
    
    userId: UUID
    
    currentTrackAt: float = Field(
        sa_column=Column("currentTrackAt", Float, nullable=False, default=0.0)
    )
    
class Shares(SQLModel, table=True):
    __tablename__ = "Shares"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    fileId: Optional[UUID] = Field(
        sa_column=Column("fileId", ForeignKey("Files.id", ondelete="CASCADE"), nullable=True)
    )
    folderId: Optional[UUID] = Field(
        sa_column=Column("folderId", ForeignKey("Folders.id", ondelete="CASCADE"), nullable=True)
    )

    sharedWithUserId: Optional[UUID] = Field(default=None, nullable=True)  # For internal user sharing
    sharedByUserId: UUID

    permission: str = Field(sa_column=Column("permission", String(length=20), nullable=False))

    sharedAt: datetime = Field(default_factory=datetime.now(), sa_column=Column(DateTime, nullable=False))

    isPublic: bool = Field(default=False, sa_column=Column("isPublic", Boolean, nullable=False))
    accessToken: Optional[str] = Field(default=None, nullable=True)
    expiresAt: Optional[datetime] = Field(default=None, nullable=True) 