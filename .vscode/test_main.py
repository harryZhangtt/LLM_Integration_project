import unittest
import requests
from util import delete_all_users
from database import SessionLocal
"""before running testcase, listen to this port 'uvicorn main:app --reload --port 8080'
    """
BASE_URL = "http://127.0.0.1:8080"
CHATGPT_API_KEY = "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"

class TestUserEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up the test environment by deleting all existing users."""
        db = SessionLocal()
        try:
            result = delete_all_users(db)
            print(result)  # Debugging print to confirm deletion
        finally:
            db.close()

    def test_create_user(self):
        """Test creating a user."""
        sample_user = {"email": "sampleuser3@example.com", "username": "sampleuser3"}
        response = requests.post(f"{BASE_URL}/users/", json=sample_user)
        self.assertEqual(response.status_code, 200, f"Failed to create user: {response.json()}")
        user_id = response.json().get("id")
        self.assertIsNotNone(user_id, "User ID not returned after creation.")

    def test_get_user_chat_rooms(self):
        """Test retrieving chat rooms for a user."""
        sample_user = {"email": "testuser@example.com", "username": "testuser"}
        response = requests.post(f"{BASE_URL}/users/", json=sample_user)
        self.assertEqual(response.status_code, 200, f"Failed to create user: {response.json()}")
        user_id = response.json().get("id")
        self.assertIsNotNone(user_id, "User ID not returned after creation.")

        response = requests.get(f"{BASE_URL}/users/{user_id}/chat_rooms/")
        self.assertEqual(response.status_code, 200, f"Failed to retrieve chat rooms: {response.json()}")
        self.assertEqual(response.json(), {"user_id": user_id, "chat_rooms": []}, "Chat rooms should be empty initially.")

    def test_get_user_chat_histories(self):
        """Test retrieving chat histories for a user."""
        sample_user = {"email": "historyuser@example.com", "username": "historyuser"}
        response = requests.post(f"{BASE_URL}/users/", json=sample_user)
        self.assertEqual(response.status_code, 200, f"Failed to create user: {response.json()}")
        user_id = response.json().get("id")
        self.assertIsNotNone(user_id, "User ID not returned after creation.")

        response = requests.get(f"{BASE_URL}/users/{user_id}/chat_histories/")
        self.assertEqual(response.status_code, 200, f"Failed to retrieve chat histories: {response.json()}")
        self.assertEqual(response.json(), {"user_id": user_id, "chat_histories": []}, "Chat histories should be empty initially.")

    def test_create_chat_room(self):
        """Test creating a chat room for a user."""
        sample_user = {"email": "sampleuser3@example.com", "username": "sampleuser3"}
        response = requests.post(f"{BASE_URL}/users/", json=sample_user)
        self.assertEqual(response.status_code, 200, f"Failed to create user: {response.json()}")
        user_id = response.json().get("id")
        self.assertIsNotNone(user_id, "User ID not returned after creation.")

        sample_chat_room = {"title": "Sample Chat Room", "owner_id": user_id}
        response = requests.post(f"{BASE_URL}/chat_rooms/", json=sample_chat_room)
        self.assertEqual(response.status_code, 200, f"Failed to create chat room: {response.json()}")

        response = requests.get(f"{BASE_URL}/users/{user_id}/chat_rooms/")
        self.assertEqual(response.status_code, 200, f"Failed to retrieve chat rooms: {response.json()}")
        chat_rooms = response.json().get("chat_rooms", [])
        self.assertEqual(len(chat_rooms), 1, "Chat rooms should contain one entry.")

    def test_create_chat_history(self):
        """Test creating a chat history for a user."""
        sample_user = {"email": "sampleuser3@example.com", "username": "sampleuser3"}
        response = requests.post(f"{BASE_URL}/users/", json=sample_user)
        self.assertEqual(response.status_code, 200, f"Failed to create user: {response.json()}")
        user_id = response.json().get("id")
        self.assertIsNotNone(user_id, "User ID not returned after creation.")

        sample_chat_room = {"title": "Sample Chat Room", "owner_id": user_id}
        response = requests.post(f"{BASE_URL}/chat_rooms/", json=sample_chat_room)
        self.assertEqual(response.status_code, 200, f"Failed to create chat room: {response.json()}")
        chat_rooms = requests.get(f"{BASE_URL}/users/{user_id}/chat_rooms/").json().get("chat_rooms", [])
        self.assertEqual(len(chat_rooms), 1, "Chat rooms should contain one entry.")

        sample_chat_history = {
            "user_id": user_id,
            "chat_room_id": chat_rooms[0]["id"],
            "archived_at": "2023-01-01T00:00:00"
        }
        response = requests.post(f"{BASE_URL}/chat_histories/", json=sample_chat_history)
        self.assertEqual(response.status_code, 200, f"Failed to create chat history: {response.json()}")

        response = requests.get(f"{BASE_URL}/users/{user_id}/chat_histories/")
        self.assertEqual(response.status_code, 200, f"Failed to retrieve chat histories: {response.json()}")
        chat_histories = response.json().get("chat_histories", [])
        self.assertEqual(len(chat_histories), 1, "Chat histories should contain one entry.")

    def test_intensive_user_creation(self):
        """Test creating a large number of users."""
        num_users = 1000  # Adjust the number as needed for intensive testing
        created_user_ids = []

        for i in range(num_users):
            sample_user = {"email": f"user{i}@example.com", "username": f"user{i}"}
            response = requests.post(f"{BASE_URL}/users/", json=sample_user)
            self.assertEqual(response.status_code, 200, f"Failed to create user {i}: {response.json()}")
            user_id = response.json().get("id")
            self.assertIsNotNone(user_id, f"User ID not returned for user {i}")
            created_user_ids.append(user_id)

        self.assertEqual(len(created_user_ids), num_users, "Not all users were created successfully.")

    def test_intensive_chat_room_creation(self):
        """Test creating a large number of chat rooms for a single user."""
        # Create a single user
        sample_user = {"email": "chatroomuser@example.com", "username": "chatroomuser"}
        response = requests.post(f"{BASE_URL}/users/", json=sample_user)
        self.assertEqual(response.status_code, 200, f"Failed to create user: {response.json()}")
        user_id = response.json().get("id")
        self.assertIsNotNone(user_id, "User ID not returned after creation.")

        num_chat_rooms = 500  # Adjust the number as needed for intensive testing
        created_chat_room_ids = []

        for i in range(num_chat_rooms):
            sample_chat_room = {"title": f"Chat Room {i}", "owner_id": user_id}
            response = requests.post(f"{BASE_URL}/chat_rooms/", json=sample_chat_room)
            self.assertEqual(response.status_code, 200, f"Failed to create chat room {i}: {response.json()}")
            chat_room_id = response.json().get("id")
            self.assertIsNotNone(chat_room_id, f"Chat Room ID not returned for chat room {i}")
            created_chat_room_ids.append(chat_room_id)

        response = requests.get(f"{BASE_URL}/users/{user_id}/chat_rooms/")
        self.assertEqual(response.status_code, 200, f"Failed to retrieve chat rooms: {response.json()}")
        chat_rooms = response.json().get("chat_rooms", [])
        self.assertEqual(len(chat_rooms), num_chat_rooms, "Not all chat rooms were created successfully.")

    def test_intensive_chat_history_creation(self):
        """Test creating a large number of chat histories for a single user and chat room."""
        # Create a single user
        sample_user = {"email": "historyuser@example.com", "username": "historyuser"}
        response = requests.post(f"{BASE_URL}/users/", json=sample_user)
        self.assertEqual(response.status_code, 200, f"Failed to create user: {response.json()}")
        user_id = response.json().get("id")
        self.assertIsNotNone(user_id, "User ID not returned after creation.")

        # Create a single chat room
        sample_chat_room = {"title": "History Chat Room", "owner_id": user_id}
        response = requests.post(f"{BASE_URL}/chat_rooms/", json=sample_chat_room)
        self.assertEqual(response.status_code, 200, f"Failed to create chat room: {response.json()}")
        chat_room_id = response.json().get("id")
        self.assertIsNotNone(chat_room_id, "Chat Room ID not returned after creation.")

        num_chat_histories = 1000  # Adjust the number as needed for intensive testing
        created_chat_history_ids = []

        for i in range(num_chat_histories):
            sample_chat_history = {
                "user_id": user_id,
                "chat_room_id": chat_room_id,
                "archived_at": f"2023-01-01T00:00:{i % 60:02d}"  # Vary the archived_at timestamp
            }
            response = requests.post(f"{BASE_URL}/chat_histories/", json=sample_chat_history)
            self.assertEqual(response.status_code, 200, f"Failed to create chat history {i}: {response.json()}")
            chat_history_id = response.json().get("id")
            self.assertIsNotNone(chat_history_id, f"Chat History ID not returned for chat history {i}")
            created_chat_history_ids.append(chat_history_id)

        response = requests.get(f"{BASE_URL}/users/{user_id}/chat_histories/")
        self.assertEqual(response.status_code, 200, f"Failed to retrieve chat histories: {response.json()}")
        chat_histories = response.json().get("chat_histories", [])
        self.assertEqual(len(chat_histories), num_chat_histories, "Not all chat histories were created successfully.")

    def test_user_chat_flow(self):
        """Test creating a user, creating a chat room, sending a message, and storing the response in chat history."""
        # Step 1: Create a user
        sample_user = {
            "email": "flowuser@example.com",
            "username": "flowuser"
        }
        response = requests.post(f"{BASE_URL}/users/", json=sample_user)
        self.assertEqual(response.status_code, 200, f"Failed to create user: {response.json()}")
        user_id = response.json().get("id")
        self.assertIsNotNone(user_id, "User ID not returned after creation.")

        # Step 2: Create a chat room
        sample_chat_room = {"title": "Flow Test Room", "owner_id": user_id}
        response = requests.post(f"{BASE_URL}/chat_rooms/", json=sample_chat_room)
        self.assertEqual(response.status_code, 200, f"Failed to create chat room: {response.json()}")
        chat_room_id = response.json().get("id")
        self.assertIsNotNone(chat_room_id, "Chat Room ID not returned after creation.")

        # Step 3: Send a message to the chat room
        from openai import OpenAI

        # Initialize the OpenAI client
        try:
            client = OpenAI(api_key=CHATGPT_API_KEY)
        except Exception as e:
            self.fail(f"Failed to initialize OpenAI client. Error: {e}")

        # Define the request payload
        payload = {
            "model": "gpt-4o",  # Ensure this model is available for your API key
            "messages": [
                {
                    "role": "user",
                    "content": "Hi, how are you?"
                }
            ]
        }

        # Send the request and handle the response
        try:
            completion = client.chat.completions.create(**payload)
            chat_response = completion.choices[0].message.content
            self.assertIsNotNone(chat_response, "ChatGPT response not returned.")
            print(f"ChatGPT Response: {chat_response}")  # Debugging print
        except Exception as e:
            self.fail(f"Failed to get a response from the OpenAI API. Error: {e}")

        # Step 4: Verify the chat history
        response = requests.get(f"{BASE_URL}/users/{user_id}/chat_histories/")
        print("Chat History API Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response JSON: {response.json()}")

        self.assertEqual(response.status_code, 200, f"Failed to retrieve chat histories: {response.json()}")
        chat_histories = response.json().get("chat_histories", [])
        self.assertEqual(len(chat_histories), 1, "Chat histories should contain one entry.")
        print(f"Chat History: {chat_histories}")  # Debugging print

if __name__ == "__main__":
    print("Running all test cases...")
    unittest.main()