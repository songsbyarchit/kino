import requests
import os

WEBEX_TOKEN = os.getenv("WEBEX_BOT_TOKEN")
WEBEX_HEADERS = {
    "Authorization": f"Bearer {WEBEX_TOKEN}",
    "Content-Type": "application/json"
}

def send_card(room_id, card_json, markdown="Here's a card"):
    response = requests.post(
        "https://webexapis.com/v1/messages",
        headers=WEBEX_HEADERS,
        json={
            "roomId": room_id,
            "markdown": markdown,
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": card_json
                }
            ]
        }
    )
    print("CARD STATUS:", response.status_code)
    print("CARD RESPONSE:", response.json())
    return response