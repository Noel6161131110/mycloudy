from fastapi import HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from ..models.models import Users
from src.database.db import get_session
from ..schemas import *
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashPassword(password: str) -> str:
    from src import SECRET_KEY

    return pwd_context.hash(password + SECRET_KEY)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    from src import SECRET_KEY

    try:
        return pwd_context.verify(plain_password + SECRET_KEY, hashed_password)
    except Exception as e:
        print(e)
        return False

def getUsers(db: Session = Depends(get_session)):
    try:
        users = db.exec(select(Users)).all()
        users_data = [UsersGetSchema.model_validate(user).model_dump(mode="json") for user in users]

        return JSONResponse(content={"users": users_data}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def createUser(user: UserCreateSchema, db: Session = Depends(get_session)):
    try:
        
        
        users = db.exec(select(Users).where(Users.email == user.email)).all()
        if users:
            raise HTTPException(status_code=400, detail="User already exists")
        
        users = db.exec(select(Users)).all()
        

        if not users:
            user.role = "admin"
            user.is_active = True
            user.password = hashPassword(user.password)
        elif not user.role or user.role not in ["admin", "member"]:
            user.role = "member"
            user.is_active = False
            user.password = ""
        else:    
            user.password = ""
            
        newUser = Users(**user.dict())
        db.add(newUser)
        db.commit()
        return JSONResponse(content={"message": "User created successfully!"}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
def loginUser(user: UsersLoginSchema, db: Session = Depends(get_session)):
    try:
        userInstance = db.exec(select(Users).where(Users.email == user.email)).first()

        if not userInstance:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not verify_password(user.password, userInstance.password):
            return JSONResponse(content={"message": "Invalid credentials"}, status_code=401)
        
        return JSONResponse(content={"message": "Login successful!"}, status_code=200)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
    
def updateUser(id: int, user: UserUpdateSchema, db: Session = Depends(get_session)):
    try:
        userInstance = db.get(Users, id)
        if not userInstance:
            raise HTTPException(status_code=404, detail="User not found")

        # Update fields
        for key, value in user.dict(exclude_unset=True).items():
            setattr(userInstance, key, value)
        
        db.commit()
        db.refresh(userInstance)  # Refresh instance to get latest DB state

        return JSONResponse(content={"message": "User updated successfully!"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
def UpdatePassword(id: int, password: PasswordUpdateSchema, db: Session = Depends(get_session)):
    try:
        userInstance = db.get(Users, id)
        if not userInstance:
            raise HTTPException(status_code=404, detail="User not found")

        userInstance.password = hashPassword(password.password)
        db.commit()
        db.refresh(userInstance)  # Refresh instance to get latest DB state

        return JSONResponse(content={"message": "Password updated successfully!"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
def deleteUser(id: int, db: Session = Depends(get_session)):
    try:
        userInstance = db.get(Users, id)
        if not userInstance:
            raise HTTPException(status_code=404, detail="User not found")

        db.delete(userInstance)
        db.commit()

        return JSONResponse(content={"message": "User deleted successfully!"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))