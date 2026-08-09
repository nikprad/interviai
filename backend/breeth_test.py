import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BREETH_API_KEY")

if not API_KEY:
    print("ERROR: BREETH_API_KEY not found in .env")
    exit()

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

data = {
    "content": "InterviAI is an AI-powered interview platform that conducts conversational interviews and provides personalized feedback.",
    "group_id": "interviai",
    "extract_intent": True,
}

response = requests.post(
    "https://api.thebreeth.com/v1/episodes",
    headers=headers,
    json=data,
)

print("Status:", response.status_code)
print("Response:", response.json())