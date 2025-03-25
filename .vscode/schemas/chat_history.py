from pydantic import BaseModel
from datetime import datetime

class ChatHistoryBase(BaseModel):
    archived_at: datetime

class ChatHistoryCreate(ChatHistoryBase):
    user_id: int
    chat_room_id: int

class ChatHistoryResponse(ChatHistoryBase):
    id: int
    user_id: int
    chat_room_id: int

    class Config:
        orm_mode = True
