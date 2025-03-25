from sqlalchemy.orm import Session
from ORM_model.user import User
from ORM_model.chat_room import ChatRoom
from ORM_model.chat_history import ChatHistory

def delete_all_users(db: Session):
    """Delete all users and their dependent records from the database."""
    try:
        # Delete dependent records first to satisfy foreign key constraints
        deleted_chat_histories = db.query(ChatHistory).delete()
        deleted_chat_rooms = db.query(ChatRoom).delete()
        deleted_users = db.query(User).delete()
        db.commit()
        print(f"Deleted {deleted_chat_histories} chat histories, {deleted_chat_rooms} chat rooms, and {deleted_users} users.")  # Debugging print
        return {
            "message": f"Deleted {deleted_chat_histories} chat histories, {deleted_chat_rooms} chat rooms, and {deleted_users} users."
        }
    except Exception as e:
        print(f"Error deleting users and related records: {e}")  # Debugging print
        raise Exception(f"Error deleting users and related records: {e}")
