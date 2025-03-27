import unittest
import requests
from util import delete_all_users
from database import SessionLocal

BASE_URL = "http://127.0.0.1:8080"

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
        user_message = "Hi, how are you?"
        message_payload = {
            "name": "test1",  # Match the key name in the systematic_api_key field
            "key": "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"
        }
        response = requests.post(
            f"{BASE_URL}/users/{user_id}/chat_rooms/{chat_room_id}/messages_with_key/",
            params={"message": user_message},
            json=message_payload
        )

        # Debugging steps for failure
        if response.status_code != 200:
            print("Failed to send message:")
            print(f"Status Code: {response.status_code}")
            print(f"Response JSON: {response.json()}")
            print(f"Request URL: {response.request.url}")
            print(f"Request Headers: {response.request.headers}")
            print(f"Request Body: {response.request.body}")

        self.assertEqual(response.status_code, 200, f"Failed to send message: {response.json()}")
        chat_response = response.json().get("chatgpt_response")
        self.assertIsNotNone(chat_response, "ChatGPT response not returned.")
        print(f"ChatGPT Response: {chat_response}")  # Debugging print

        # Step 4: Verify the chat history
        response = requests.get(f"{BASE_URL}/users/{user_id}/chat_histories/")
        self.assertEqual(response.status_code, 200, f"Failed to retrieve chat histories: {response.json()}")
        chat_histories = response.json().get("chat_histories", [])
        self.assertEqual(len(chat_histories), 1, "Chat histories should contain one entry.")
        print(f"Chat History: {chat_histories}")  # Debugging print

if __name__ == "__main__":
    print("Running all test cases...")
    unittest.main()