import os
import requests
from dotenv import load_dotenv

load_dotenv()

BREETH_API_KEY = os.getenv("BREETH_API_KEY")

BASE_URL = "https://api.thebreeth.com/v1"

HEADERS = {
    "Authorization": f"Bearer {BREETH_API_KEY}",
    "Content-Type": "application/json",
}


def save_memory(content, session_id):
    """Save an interview memory to Breeth."""

    if not BREETH_API_KEY:
        return None

    payload = {
        "content": content,
        "group_id": "interviai",
        "extract_intent": True,
    }

    try:
        response = requests.post(
            f"{BASE_URL}/episodes",
            headers=HEADERS,
            json=payload,
            timeout=10,
        )

        if response.ok:
            return response.json()

        print("Breeth write error:", response.status_code)
        return None

    except Exception as e:
        print("Breeth connection error:", e)
        return None


def search_memory(query):
    """Retrieve relevant memories from Breeth."""

    if not BREETH_API_KEY:
        return []

    payload = {
        "query": query,
        "limit": 5,
    }

    try:
        response = requests.post(
            f"{BASE_URL}/search",
            headers=HEADERS,
            json=payload,
            timeout=10,
        )

        if response.ok:
            data = response.json()
            return data

        print("Breeth search error:", response.status_code)
        return []

    except Exception as e:
        print("Breeth search connection error:", e)
        return []