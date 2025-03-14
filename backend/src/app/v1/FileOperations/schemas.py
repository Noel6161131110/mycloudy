from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class FileSchema(BaseModel):
    id: Optional[int] = None
    title: str
    filename: str
    file_extension: str
    file_path: str
    file_type: str
    total_length: Optional[float] = None
    current_track_at: Optional[float] = None
    uploaded_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None
    last_updated_by: Optional[str] = None

    class Config:
        from_attributes = True  # Required for SQLModel compatibility