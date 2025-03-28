from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()
WEBEX_TOKEN = os.getenv("WEBEX_BOT_TOKEN")

app = Flask(__name__)

@app.route("/messages", methods=["POST"])
def messages():
    data = request.json
    if data["resource"] == "messages" and data["event"] == "created":
        message_id = data["data"]["id"]
        sender = data["data"]["personEmail"]

        if sender != "your-bot-email@webex.bot":
            message = requests.get(
                f"https://webexapis.com/v1/messages/{message_id}",
                headers={"Authorization": f"Bearer {WEBEX_TOKEN}"}
            ).json()["text"]

            requests.post(
                "https://webexapis.com/v1/messages",
                json={"roomId": data["data"]["roomId"], "text": f"You said: {message}"},
                headers={"Authorization": f"Bearer {WEBEX_TOKEN}"}
            )
    return "OK"