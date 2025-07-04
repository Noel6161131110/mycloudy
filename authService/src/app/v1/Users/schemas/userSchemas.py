from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class UsersGetSchema(BaseModel):
    id: Optional[UUID] = None
    firstName: str
    lastName: str
    email: str
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    lastLogin: Optional[datetime] = None

    class Config:
        from_attributes = True
        
        
class UserCreateSchema(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str

    class Config:
        from_attributes = True
        
        
class InviteUserCreateSchema(BaseModel):
    linkToken: str
    firstName: str
    lastName: str
    password: str
    
    class Config:
        from_attributes = True

class UserUpdateSchema(BaseModel):
    id: UUID
    firstName: str
    lastName: str
    email: str

    class Config:
        from_attributes = True
        
        
class PasswordUpdateSchema(BaseModel):
    id: UUID
    password: str

    class Config:
        from_attributes = True
        
class UserIdSchema(BaseModel):
    id: UUID

    class Config:
        from_attributes = True