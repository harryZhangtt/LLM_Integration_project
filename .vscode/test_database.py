from database import engine, Base

# Import your models here
from ORM_model.user import User
from ORM_model.chat_history import ChatHistory

# Create all tables in the database
print("Connecting to the PostgreSQL database...")
try:
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully in the PostgreSQL database!")
except Exception as e:
    print(f"Error creating tables: {e}")
