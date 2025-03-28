from flask import Flask, request
from dotenv import load_dotenv
from cards.homepage import get_homepage_card
from cards.feature_selector import get_feature_selector_card
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

    elif data["resource"] == "attachmentActions" and data["event"] == "created":
        room_id = data["data"]["roomId"]
        action_id = data["data"]["id"]

        # Get the data from the submitted action
        action_details = requests.get(
            f"https://webexapis.com/v1/attachment/actions/{action_id}",
            headers={"Authorization": f"Bearer {WEBEX_TOKEN}"}
        ).json()

        action_type = action_details.get("inputs", {}).get("action")
        print("User clicked:", action_type)

        if action_type == "show_features":
            send_card(room_id, get_feature_selector_card(), markdown="Choose a feature")

    return "OK"

if __name__ == "__main__":
    app.run(debug=True)