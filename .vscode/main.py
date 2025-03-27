# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from ORM_model.user import *
from ORM_model.chat_room import *
from ORM_model.chat_history import *
from schemas.user import *
from schemas.chat import *
from schemas.chat import APIKeySelect  # Ensure this import is present
from schemas.chat_history import *
from util import *  # Import delete_all_users from util.py
from services.chat_service import send_message_and_record  # Import the function
import requests

# Create all tables in the PostgreSQL database
Base.metadata.create_all(bind=engine)

app = FastAPI()

print("FastAPI server is starting...")

# Dependency to provide a database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(
        email=user.email,
        username=user.username,
        subscription_status=None,  # Default value for subscription_status
        systematic_api_key={  # Specify the systematic API key dictionary
            "test1": "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"
        },
        customized_api_key=None  # Default value for customized_api_key
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(f"User created successfully: {new_user.email}, ID: {new_user.id}, API Keys: {new_user.systematic_api_key}")  # Debugging print
    return new_user

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    print(f"User retrieved successfully: {user.email}, ID: {user.id}")  # Debugging print
    return user

@app.get("/users/{user_id}/chat_rooms/")
def get_user_chat_rooms(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    chat_rooms = user.get_chat_rooms(db)
    return {"user_id": user_id, "chat_rooms": [{"id": room.id, "title": room.title} for room in chat_rooms]}

@app.get("/users/{user_id}/chat_histories/")
def get_user_chat_histories(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    print(f"User found: {user.username}, ID: {user.id}")  # Debugging print
    try:
        chat_histories = user.get_chat_histories(db)
        if not chat_histories:
            print(f"No chat histories found for user ID {user_id}.")  # Debugging print
            return {"user_id": user_id, "chat_histories": []}
        print(f"Chat histories retrieved for user ID {user_id}: {chat_histories}")  # Debugging print
        return {"user_id": user_id, "chat_histories": [history.get_details(db) for history in chat_histories]}
    except Exception as e:
        print(f"Error retrieving chat histories for user ID {user_id}: {e}")  # Debugging print
        raise HTTPException(status_code=500, detail=f"Error retrieving chat histories for user ID {user_id}: {e}")

@app.post("/chat_rooms/", response_model=ChatRoomResponse)
def create_chat_room(chat_room: ChatRoomCreate, db: Session = Depends(get_db)):
    user = db.query(User).get(chat_room.owner_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_chat_room = ChatRoom(
        title=chat_room.title,
        owner_id=chat_room.owner_id
    )
    db.add(new_chat_room)
    db.commit()
    db.refresh(new_chat_room)
    print(f"Chat room created successfully: {new_chat_room.title}, ID: {new_chat_room.id}")  # Debugging print
    return new_chat_room

@app.post("/chat_histories/", response_model=ChatHistoryResponse)
def create_chat_history(chat_history: ChatHistoryCreate, db: Session = Depends(get_db)):
    user = db.query(User).get(chat_history.user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {chat_history.user_id} not found")
    chat_room = db.query(ChatRoom).get(chat_history.chat_room_id)
    if not chat_room:
        raise HTTPException(status_code=404, detail=f"Chat room with ID {chat_history.chat_room_id} not found")
    try:
        new_chat_history = ChatHistory(
            user_id=chat_history.user_id,
            chat_room_id=chat_history.chat_room_id,
            archived_at=chat_history.archived_at
        )
        db.add(new_chat_history)
        db.commit()
        db.refresh(new_chat_history)
        print(f"Chat history created successfully: ID={new_chat_history.id}")  # Debugging print
        return new_chat_history
    except Exception as e:
        print(f"Error creating chat history: {e}")  # Debugging print
        raise HTTPException(status_code=500, detail=f"Error creating chat history: {e}")

@app.delete("/users/")
def delete_all_users_endpoint(db: Session = Depends(get_db)):
    """Endpoint to delete all users and their dependent records."""
    try:
        return delete_all_users(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users/{user_id}/chat_rooms/{chat_room_id}/messages_with_key/")
def send_message_with_key(user_id: int, chat_room_id: int, message: str, api_key: APIKeySelect, db: Session = Depends(get_db)):
    """
    Send a message to ChatGPT using the provided API key and record the response.
    """
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    chat_room = db.query(ChatRoom).get(chat_room_id)
    if not chat_room:
        raise HTTPException(status_code=404, detail="Chat room not found")
    try:
        # Debugging: Print the user's API keys
        print(f"User's API Keys: {user.systematic_api_key}")  # Debugging print

        # Retrieve the API key using the provided name
        selected_api_key = user.get_systematic_api_key(api_key.name)

        # Call the send_message_and_record function with the selected API key
        response = send_message_and_record(user_id, chat_room_id, message, db, selected_api_key)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import requests

    # Update the base URL to match the actual running FastAPI server
    """before running this script, make sure to run the FastAPI server in a separate terminal with 
    'uvicorn main:app --reload --port 8080' command.
    """
    BASE_URL = "http://127.0.0.1:8080"  # Changed to port 8080 for example

    try:
        # Check if the server is running
        print(f"Checking server status at {BASE_URL}...")
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("FastAPI server is running. Proceeding with tests...")
        else:
            print(f"FastAPI server is not responding as expected. Status code: {response.status_code}")
            exit(1)
    except requests.exceptions.ConnectionError as e:
        print(f"FastAPI server is not running. Error: {e}")
        print("Please start the server with 'uvicorn main:app --reload --port 8080'.")
        exit(1)

    # Delete all existing users
    print("Deleting all existing users...")
    response = requests.delete(f"{BASE_URL}/users/")
    if response.status_code != 200:
        raise Exception(f"Failed to delete all users: {response.json()}")
    print("Response from delete_all_users:", response.json())

    # Sample user creation for testing
    sample_user = {
        "email": "sampleuser3@example.com",
        "username": "sampleuser3"
    }
    print("Creating a sample user...")
    response = requests.post(f"{BASE_URL}/users/", json=sample_user)
    print("Response from create_user:", response.json())

    user_id = response.json().get("id")
    if user_id:
        # Test retrieving chat rooms for the user
        print("Retrieving chat rooms for the user...")
        response = requests.get(f"{BASE_URL}/users/{user_id}/chat_rooms/")
        print("Response from get_user_chat_rooms:", response.json())

        # Test retrieving chat histories for the user
        print("Retrieving chat histories for the user...")
        response = requests.get(f"{BASE_URL}/users/{user_id}/chat_histories/")
        print("Response from get_user_chat_histories:", response.json())

        # Add a sample chat room for the user
        print("Adding a sample chat room...")
        sample_chat_room = {
            "title": "Sample Chat Room",
            "owner_id": user_id
        }
        response = requests.post(f"{BASE_URL}/chat_rooms/", json=sample_chat_room)
        print("Response from create_chat_room:", response.json())

        # Retrieve chat rooms again
        print("Retrieving chat rooms for the user after adding a chat room...")
        response = requests.get(f"{BASE_URL}/users/{user_id}/chat_rooms/")
        chat_rooms = response.json().get("chat_rooms", [])
        print("Response from get_user_chat_rooms:", response.json())

        if not chat_rooms:
            print("No chat rooms found after creation. Exiting test.")
            exit(1)

        # Add a sample chat history for the user
        print("Adding a sample chat history...")
        sample_chat_history = {
            "user_id": user_id,
            "chat_room_id": chat_rooms[0]["id"],  # Assuming the first chat room
            "archived_at": "2023-01-01T00:00:00"
        }
        response = requests.post(f"{BASE_URL}/chat_histories/", json=sample_chat_history)
        print("Response from create_chat_history:", response.json())

        # Retrieve chat histories again
        print("Retrieving chat histories for the user after adding a chat history...")
        response = requests.get(f"{BASE_URL}/users/{user_id}/chat_histories/")
        print("Response from get_user_chat_histories:", response.json())
