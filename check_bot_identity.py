import requests
from dotenv import load_dotenv
import os

load_dotenv()
WEBEX_TOKEN = os.getenv("WEBEX_BOT_TOKEN")

response = requests.get(
    "https://webexapis.com/v1/people/me",
    headers={"Authorization": f"Bearer {WEBEX_TOKEN}"}
)

print("🔁 Status code:", response.status_code)
print("🔍 Response:", response.json())