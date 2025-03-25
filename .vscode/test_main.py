import unittest
import requests

BASE_URL = "http://127.0.0.1:8080"

class TestUserEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up the test environment by deleting all existing users."""
        response = requests.delete(f"{BASE_URL}/users/")
        self.assertEqual(response.status_code, 200, f"Failed to delete all users: {response.json()}")

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

if __name__ == "__main__":
    print("Running all test cases...")
    unittest.main()