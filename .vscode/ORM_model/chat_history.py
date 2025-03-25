# ORM_model/chat_history.py
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Session
from database import Base
from .chat_room import ChatRoom  # Import ChatRoom model

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    archived_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships using string names to avoid circular imports
    user = relationship("User", back_populates="chat_histories")
    chat_room = relationship("ChatRoom", back_populates="history")

    def get_details(self, db: Session):
        """Retrieve details of the chat history, including user and chat room."""
        from .user import User  # Import locally to avoid circular import
        try:
            user = db.query(User).filter(User.id == self.user_id).first()
            if not user:
                raise Exception(f"User with ID {self.user_id} not found")
            chat_room = db.query(ChatRoom).filter(ChatRoom.id == self.chat_room_id).first()
            if not chat_room:
                raise Exception(f"Chat room with ID {self.chat_room_id} not found")
            print(f"ChatHistory.get_details: user={user}, chat_room={chat_room}")  # Debugging print
            return {
                "id": self.id,
                "user": user.username if user else None,
                "chat_room": chat_room.title if chat_room else None,
                "archived_at": self.archived_at
            }
        except Exception as e:
            print(f"Error in ChatHistory.get_details: {e}")  # Debugging print
            raise Exception(f"Error in ChatHistory.get_details: {e}")
