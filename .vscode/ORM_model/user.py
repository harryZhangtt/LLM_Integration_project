# models.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship, Session  # Import Session
from .chat_room import ChatRoom  # Import ChatRoom model

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())
    #systematic LLM ModelAPI key
    systematic_api_key = Column(JSON, nullable=True)
    #customized LLM Model API key
    customized_api_key = Column(JSON, nullable=True)
    subscription_status = Column(String, nullable=True)
    
    # One-to-many: A user can have many chat rooms.
    chat_rooms = relationship("ChatRoom", back_populates="owner", cascade="all, delete-orphan")
    # Optionally, if you want to store chat history separately:
    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")

    def get_chat_rooms(self, db: Session):
        """Retrieve all chat rooms owned by the user."""
        return db.query(ChatRoom).filter(ChatRoom.owner_id == self.id).all()

    def get_chat_histories(self, db: Session):
        """Retrieve all chat histories associated with the user."""
        from .chat_history import ChatHistory  # Import locally to avoid circular import
        return db.query(ChatHistory).filter(ChatHistory.user_id == self.id).all()

    def set_systematic_api_key(self, key_name: str, key_value: str):
        """
        Set a systematic API key for the user.
        """
        if not self.systematic_api_key:
            self.systematic_api_key = {}
        self.systematic_api_key[key_name] = key_value

    def get_systematic_api_key(self, key_name: str) -> str:
        """
        Get a systematic API key by its name.
        """
        if not self.systematic_api_key or key_name not in self.systematic_api_key:
            raise ValueError(f"API key name '{key_name}' not found.")
        return self.systematic_api_key[key_name]
