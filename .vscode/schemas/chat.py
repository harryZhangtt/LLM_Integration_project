# schemas/chat.py
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"

class ChatMessageBase(BaseModel):
    sender: MessageRole
    message: str

class ChatMessageResponse(ChatMessageBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class ChatRoomBase(BaseModel):
    title: Optional[str]

class ChatRoomCreate(ChatRoomBase):
    owner_id: int

class ChatRoomResponse(ChatRoomBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessageResponse] = []

    class Config:
        from_attributes = True
