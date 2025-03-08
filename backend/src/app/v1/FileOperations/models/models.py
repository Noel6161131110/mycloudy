from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, Dict


class FileModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    filename: str
    file_extension: str
    file_path: str
    file_type: str
    total_length: Optional[float] = None
    current_track_at: Optional[float] = None
    uploaded_at: Optional[str] = Field(default=None)