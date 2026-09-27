"""
db.py — MongoDB connection for Task AI

Connection string resolution order:
  1. st.secrets["MONGODB_URI"]   (recommended — see .streamlit/secrets.toml.example)
  2. environment variable MONGODB_URI
  3. fallback: mongodb://localhost:27017  (local MongoDB instance)

Database name resolution order:
  1. st.secrets["MONGODB_DB"]
  2. environment variable MONGODB_DB
  3. fallback: "task_ai"
"""

import os
import streamlit as st
import certifi
from pymongo import MongoClient


def _get_setting(key: str, default: str) -> str:
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)


@st.cache_resource(show_spinner=False)
def get_client() -> MongoClient:
    uri = _get_setting("MONGODB_URI", "mongodb://localhost:27017")
    return MongoClient(uri, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())


def get_db():
    client = get_client()
    db_name = _get_setting("MONGODB_DB", "task_ai")
    return client[db_name]


def check_connection() -> tuple[bool, str]:
    """Ping the server to confirm the connection works. Useful for a startup check."""
    try:
        get_client().admin.command("ping")
        return True, "Connected to MongoDB."
    except Exception as e:
        return False, f"Could not connect to MongoDB: {e}"