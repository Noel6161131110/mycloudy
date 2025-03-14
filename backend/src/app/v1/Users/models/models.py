from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class Users(SQLModel, table=True):
    
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=False)
    email: str = Field(max_length=50, unique=True, nullable=False)
    password: str = Field(max_length=50, nullable=False)
    role: str = Field(max_length=50, nullable=False)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: Optional[bool] = Field(default=True)