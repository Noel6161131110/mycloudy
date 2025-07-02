from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, BigInteger, ForeignKey, DateTime

class Activity(SQLModel, table=True):
    __tablename__ = "Activity"

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    fileId: UUID = Field(
        sa_column=Column("fileId", ForeignKey("Files.id"), nullable=False)
    )
    
    userId: UUID
    
    folderId: UUID = Field(
        sa_column=Column("folderId", ForeignKey("Folders.id"), nullable=False)
    )

    action: str = Field(max_length=50, nullable=False)
    
    oldValue: Optional[str] = Field(
        default=None, sa_column=Column("oldValue", Text, nullable=True)
    )
    newValue: Optional[str] = Field(
        default=None, sa_column=Column("newValue", Text, nullable=True)
    )
    

    actionTime: datetime = Field(
        sa_column=Column("actionTime", DateTime, nullable=False, default=datetime.now())
    )