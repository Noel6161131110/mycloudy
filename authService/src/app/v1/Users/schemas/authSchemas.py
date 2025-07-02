from pydantic import BaseModel


class PasswordRegisterSchema(BaseModel):
    name: str
    password: str
    
    class Config:
        from_attributes = True
      
      
class TokenSchema(BaseModel):
    token: str

    class Config:
        from_attributes = True
        
        
class UsersLoginSchema(BaseModel):
    email: str
    password: str
    
    class Config:
        from_attributes = True