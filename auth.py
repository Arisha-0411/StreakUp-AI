"""
auth.py — user signup / login for Task AI
Stores users in a local JSON file (data/users.json).
"""

import json
import os
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

os.makedirs(DATA_DIR, exist_ok=True)


def _hash_password(password: str) -> str:
    """Simple sha256 hash so passwords aren't stored in plain text."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_users(users: dict) -> None:
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def signup(username: str, password: str, full_name: str, gender: str) -> tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    if not username or not password:
        return False, "Username and password are required."

    users = load_users()
    if username in users:
        return False, "That username is already taken."

    users[username] = {
        "password": _hash_password(password),
        "full_name": full_name or username,
        "gender": gender,  # "male" or "female" -> drives avatar choice
    }
    save_users(users)
    return True, "Account created successfully! Please log in."


def login(username: str, password: str) -> tuple[bool, str]:
    """Validate credentials. Returns (success, message)."""
    users = load_users()
    if username not in users:
        return False, "No account found with that username."

    if users[username]["password"] != _hash_password(password):
        return False, "Incorrect password."

    return True, "Logged in successfully!"


def get_user_profile(username: str) -> dict:
    users = load_users()
    return users.get(username, {})
