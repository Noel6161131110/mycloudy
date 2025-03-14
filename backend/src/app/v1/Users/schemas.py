from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class UsersGetSchema(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    role: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True
        
        
class UserCreateSchema(BaseModel):
    name: str
    email: str
    password: str
    role: str
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True
        
        
class UserUpdateSchema(BaseModel):
    name: str
    email: str

    class Config:
        from_attributes = True
        
        
class PasswordUpdateSchema(BaseModel):
    password: str

    class Config:
        from_attributes = True
        
class UsersLoginSchema(BaseModel):
    email: str
    password: str
    
    class Config:
        from_attributes = True