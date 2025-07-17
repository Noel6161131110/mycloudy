from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column, Text
from sqlalchemy import ForeignKey, DateTime, String
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Relationship
from src.app.v1.Activity.models.tagModels import FolderTagLink

if TYPE_CHECKING:
    from src.app.v1.Activity.models.models import Tags

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
    
    tags: List["Tags"] = Relationship(back_populates="folders", link_model=FolderTagLink)
    
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
    
    softDeleted: bool = Field(default=False, nullable=False)


