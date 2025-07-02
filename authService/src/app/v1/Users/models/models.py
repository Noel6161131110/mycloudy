from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ForeignKey, DateTime


class Users(SQLModel, table=True):
    __tablename__ = "Users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    firstName: str = Field(max_length=50)
    lastName: str = Field(max_length=50)
    email: str = Field(max_length=100, unique=True)

    roleId: UUID = Field(
        sa_column=Column("roleId", ForeignKey("Roles.id"), nullable=False)
    )

    createdAt: Optional[datetime] = Field(
        sa_column=Column("createdAt", DateTime, nullable=False, default=datetime.now())
    )
    updatedAt: Optional[datetime] = Field(
        sa_column=Column("updatedAt", DateTime, nullable=False, default=datetime.now())
    )
    lastLogin: Optional[datetime] = Field(
        sa_column=Column("lastLogin", DateTime, nullable=True)
    )

class PasswordHash(SQLModel, table=True):
    __tablename__ = "PasswordHash"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    userId: UUID = Field(
        sa_column=Column("userId", ForeignKey("Users.id", ondelete="CASCADE"), nullable=False)
    )
    salt: str = Field(max_length=100, nullable=False)
    hash: str = Field(max_length=200, nullable=False)

class Roles(SQLModel, table=True):
    __tablename__ = "Roles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=100)

    createdBy: Optional[UUID] = Field(
        default=None,
        sa_column=Column("createdBy", ForeignKey("Users.id", ondelete="SET NULL"), nullable=True)
    )
    
class InviteLink(SQLModel, table=True):
    __tablename__ = "InviteLinks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    linkToken: str = Field(max_length=200, unique=True, nullable=False)
    createdBy: UUID = Field(
        sa_column=Column("createdBy", ForeignKey("Users.id", ondelete="CASCADE"), nullable=False)
    )
    validTill: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    createdAt: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    )
    emailId: str = Field(max_length=100, nullable=False)