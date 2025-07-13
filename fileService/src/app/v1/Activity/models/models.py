from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, BigInteger, ForeignKey, DateTime, String
from enum import Enum

class ActivityType(str, Enum):
    FILE = "FILE"
    FOLDER = "FOLDER"

class ActionType(str, Enum):
    CREATED = "CREATED"
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


    fileId: Optional[UUID] = Field(default=None, foreign_key="Files.id", ondelete="CASCADE")
    folderId: Optional[UUID] = Field(default=None, foreign_key="Folders.id", ondelete="CASCADE")
    
    fieldChanged: Optional[str] = Field(
        default=None, sa_column=Column("fieldChanged", String(length=50))
    )

    oldValue: Optional[str] = Field(default=None, sa_column=Column("oldValue", Text))
    newValue: Optional[str] = Field(default=None, sa_column=Column("newValue", Text))

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