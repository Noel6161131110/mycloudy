from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, BigInteger, ForeignKey, DateTime, Float, String

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
        sa_column=Column("folderId", ForeignKey("Folders.id"), nullable=False)
    )

    totalVideoLength: Optional[float] = Field(
        sa_column=Column("totalVideoLength", Float, nullable=False, default=None)
    )
    
    
    
class VideoStreamInfo(SQLModel, table=True):
    __tablename__ = "VideoStreamInfo"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    fileId: UUID = Field(
        sa_column=Column("fileId", ForeignKey("Files.id"), nullable=False)
    )
    
    userId: UUID
    
    currentTrackAt: float = Field(
        sa_column=Column("currentTrackAt", Float, nullable=False, default=0.0)
    )
    
class FileShares(SQLModel, table=True):
    __tablename__ = "FileShares"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    fileId: UUID = Field(
        sa_column=Column("fileId", ForeignKey("Files.id"), nullable=False)
    )
    
    folderId: UUID = Field(
        sa_column=Column("folderId", ForeignKey("Folders.id"), nullable=False)
    )
    
    sharedWithUserId: UUID
    
    sharedByUserId: UUID
    
    permission: str = Field(
        sa_column=Column("permission", String(length=20), nullable=False)
    )
    
    sharedAt: datetime = Field(
        sa_column=Column("sharedAt", DateTime, nullable=False, default=datetime.now())
    )