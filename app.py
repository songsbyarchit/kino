from flask import Flask, request
from dotenv import load_dotenv
from cards.homepage import get_homepage_card
from utils.webex import send_card
import os, requests

load_dotenv()
WEBEX_TOKEN = os.getenv("WEBEX_BOT_TOKEN")
BOT_ID = requests.get(
    "https://webexapis.com/v1/people/me",
    headers={"Authorization": f"Bearer {WEBEX_TOKEN}"}
).json()["id"]

app = Flask(__name__)

@app.route("/messages", methods=["POST"])
def messages():
    data = request.json
    if data["resource"] == "messages" and data["event"] == "created":
        sender_id = data["data"]["personId"]
        room_id = data["data"]["roomId"]

        if sender_id != BOT_ID:
            send_card(room_id, get_homepage_card(), markdown="Welcome to Kino")
    return "OK"

if __name__ == "__main__":
    app.run(debug=True)