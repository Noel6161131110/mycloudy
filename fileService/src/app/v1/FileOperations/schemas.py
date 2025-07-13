from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class FileSchema(BaseModel):
    id: Optional[int] = None
    title: str
    filename: str
    fileExtension: str
    filePath: str
    fileType: str
    totalLength: Optional[float] = None
    currentTrackAt: Optional[float] = None
    lastModified: Optional[datetime] = None


    class Config:
        from_attributes = True