from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ForeignKey, DateTime


class Folders(SQLModel, table=True):
    __tablename__ = "Folders"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    name: str = Field(max_length=100, nullable=False)
    description: Optional[str] = Field(max_length=200, default=None, nullable=True)
    
    parentId: Optional[UUID] = Field(
        default=None,
        sa_column=Column("parentId", ForeignKey("Folders.id"), nullable=True)
    )
    tagId: Optional[UUID] = Field(
        sa_column=Column("tagId", ForeignKey("Tags.id"), nullable=True)
    )
    createdBy: UUID

    createdAt: Optional[datetime] = Field(
        sa_column=Column("createdAt", DateTime, nullable=False, default=datetime.now())
    )
    updatedAt: Optional[datetime] = Field(
        sa_column=Column("updatedAt", DateTime, nullable=False, default=datetime.now())
    )


class Tags(SQLModel, table=True):
    __tablename__ = "Tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=100, nullable=False)
    
    createdBy: UUID

    createdAt: Optional[datetime] = Field(
        default=None, sa_column=Column("createdAt", DateTime, nullable=False, default=datetime.now())
    )
