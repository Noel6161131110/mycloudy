from pydantic import BaseModel
from typing import Optional, List

class ActivityHistorySchema(BaseModel):
    entityType: str
    action: str
    newValue: Optional[str]
    timestamp: str
    fieldChanged: Optional[str]
    oldValue: Optional[str]
    parentFolderName: Optional[str]
    message: str


class PeriodHistorySchema(BaseModel):
    periodName: str
    history: List[ActivityHistorySchema]

class ActivityResponseSchema(BaseModel):
    result: List[PeriodHistorySchema]