from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class InviteLinkCreateSchema(BaseModel):
    userId: UUID
    emailId: str
    expiryType: str
    expiryValue: int

    class Config:
        from_attributes = True
        
        
class InviteLinkGetSchema(BaseModel):
    id: UUID
    linkToken: str
    createdBy: UUID
    emailId: str
    validTill: datetime | None = None
    createdAt: datetime

    class Config:
        from_attributes = True
        
class InviteLinkDeleteSchema(BaseModel):
    userId: UUID
    id: UUID
    
    class Config:
        from_attributes = True