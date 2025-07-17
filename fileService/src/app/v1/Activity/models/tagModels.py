
from uuid import UUID
from sqlmodel import SQLModel, Field


class FileTagLink(SQLModel, table=True):
    __tablename__ = "FileTagLink"
    fileId: UUID = Field(foreign_key="Files.id", primary_key=True)
    tagId: UUID = Field(foreign_key="Tags.id", primary_key=True)
    
class FolderTagLink(SQLModel, table=True):
    __tablename__ = "FolderTagLink"
    folderId: UUID = Field(foreign_key="Folders.id", primary_key=True)
    tagId: UUID = Field(foreign_key="Tags.id", primary_key=True)