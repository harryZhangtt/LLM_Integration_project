import sys
import os
import requests
import time  # Import time for retry logic
from sqlalchemy.orm import Session
from ORM_model.chat_room import ChatRoom
from ORM_model.chat_history import ChatHistory
from ORM_model.user import User
from fastapi import HTTPException
from config import CHATGPT_API_URL  # Import the ChatGPT API URL from config

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_chat_room_for_user(user_id: int, title: str, db: Session):
    """
    Create a chat room for a user.
    """
    chat_room = ChatRoom(title=title, owner_id=user_id)
    db.add(chat_room)
    db.commit()
    db.refresh(chat_room)
    return chat_room

def send_message_and_record(user_id: int, chat_room_id: int, user_message: str, db: Session, api_key: str):
    """
    Send a message to ChatGPT using a specific API key, record the user's message and ChatGPT's response.
    Implements exponential backoff for retries in case of 429 Too Many Requests errors.
    """
    # Record the user's message
    user_message_data = {"role": "user", "content": user_message}
    messages = [user_message_data]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages
    }

    max_retries = 5  # Maximum number of retries
    backoff_factor = 2  # Exponential backoff factor
    retry_delay = 1  # Initial delay in seconds

    for attempt in range(max_retries):
        try:
            print(f"User ID: {user_id}, Chat Room ID: {chat_room_id}, API Key: {api_key}")  # Debugging print
            print(f"Sending payload to ChatGPT: {payload}")  # Debugging print
            response = requests.post(CHATGPT_API_URL, headers=headers, json=payload)
            print(f"ChatGPT Response Status Code: {response.status_code}")  # Debugging print
            print(f"ChatGPT Response Text: {response.text}")  # Debugging print
            response.raise_for_status()

            # Log API usage limits if available in headers
            if "X-RateLimit-Limit" in response.headers:
                print(f"API Usage Limit: {response.headers['X-RateLimit-Limit']}")
            if "X-RateLimit-Remaining" in response.headers:
                print(f"API Usage Remaining: {response.headers['X-RateLimit-Remaining']}")
            if "X-RateLimit-Reset" in response.headers:
                print(f"API Usage Reset Time: {response.headers['X-RateLimit-Reset']}")

            chatgpt_response = response.json()["choices"][0]["message"]["content"]
            break  # Exit the retry loop if the request is successful
        except requests.exceptions.RequestException as e:
            if response.status_code == 429 and attempt < max_retries - 1:
                print(f"429 Too Many Requests: Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= backoff_factor  # Exponentially increase the delay
            else:
                print(f"Error communicating with ChatGPT: {e}, Response: {response.text if response else 'No response'}")  # Debugging print
                raise HTTPException(status_code=500, detail=f"Error communicating with ChatGPT: {e}")

    # Record the ChatGPT response
    chatgpt_message_data = {"role": "assistant", "content": chatgpt_response}
    messages.append(chatgpt_message_data)

    # Update the database
    chat_history = ChatHistory(
        user_id=user_id,
        chat_room_id=chat_room_id,
        archived_at=None,  # Not archived yet
        messages=messages  # Store the conversation
    )
    db.add(chat_history)
    db.commit()
    db.refresh(chat_history)

    return {"user_message": user_message, "chatgpt_response": chatgpt_response}
