from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

class FileModel(SQLModel, table=True):
    
    __tablename__ = "files"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=50, unique=False)
    filename: str = Field(max_length=50, nullable=False)
    file_extension: str = Field(max_length=10, nullable=False)
    file_path: str = Field(max_length=255, nullable=False)
    file_type: str = Field(max_length=10, nullable=False)
    total_length: Optional[float] = None
    current_track_at: Optional[float] = None
    uploaded_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated_by: Optional[str] = Field(max_length=50, nullable=True)