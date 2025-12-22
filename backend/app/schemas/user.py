from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    """
    Data expected by API for user creation.
    Same as UserBase, seperated to add 
    more fields later.
    """
    password: str


class UserOut(UserBase):
    """
    Data expected by API to return to client
    when sending back user info
    """
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str