# schemas/user.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str
    username: str | None = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    email: str
    username: Optional[str]
    created_at: datetime
    updated_at: datetime
    subscription_status: Optional[str]
    systematic_api_key: Optional[dict]
    customized_api_key: Optional[dict]

    class Config:
        orm_mode = True

__all__ = ["UserBase", "UserCreate", "UserResponse"]
