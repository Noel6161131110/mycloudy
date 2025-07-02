from pydantic import BaseModel
from uuid import UUID


class UserRoleChangeSchema(BaseModel):
    userId: UUID
    roleId: UUID

    class Config:
        from_attributes = True
        
        
class RolesGetSchema(BaseModel):
    id: UUID
    name: str
    createdBy: UUID | None = None

    class Config:
        from_attributes = True