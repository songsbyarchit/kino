from flask import Flask, request
from dotenv import load_dotenv
from cards.homepage import get_homepage_card
from cards.feature_selector import get_feature_selector_card
from utils.webex import send_card
import os, requests, sys

# ✅ Load environment variables early
load_dotenv()
WEBEX_TOKEN = os.getenv("WEBEX_BOT_TOKEN")

if not WEBEX_TOKEN:
    print("❌ ERROR: WEBEX_BOT_TOKEN not found in .env file.")
    sys.exit(1)

print("🔑 Loaded token (first 20 chars):", WEBEX_TOKEN[:20])

# ✅ Fetch bot ID with error handling
response = requests.get(
    "https://webexapis.com/v1/people/me",
    headers={"Authorization": f"Bearer {WEBEX_TOKEN}"}
)

print("📡 Status code:", response.status_code)
try:
    bot_info = response.json()
    print("📨 Bot identity response:", bot_info)
    BOT_ID = bot_info["id"]
except Exception as e:
    print("❌ ERROR: Failed to fetch bot ID. Response:", response.text)
    sys.exit(1)

# ✅ Flask app
app = Flask(__name__)
room_state = {}

@app.route("/messages", methods=["POST"])
def messages():
    data = request.json
    print("📩 Incoming webhook:", data.get("resource"), "-", data.get("event"))

    if data["resource"] == "messages" and data["event"] == "created":
        sender_id = data["data"]["personId"]
        room_id = data["data"]["roomId"]

        if sender_id != BOT_ID:
            current_tool = room_state.get(room_id)

            if current_tool == "reword":
                user_message_id = data["data"]["id"]
                message_data = requests.get(
                    f"https://webexapis.com/v1/messages/{user_message_id}",
                    headers={"Authorization": f"Bearer {WEBEX_TOKEN}"}
                ).json()
                input_text = message_data.get("text", "")

                # OpenAI call
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "user", "content": f"Please reword this in a simpler way: {input_text}"}
                        ]
                    }
                ).json()

                reply = response["choices"][0]["message"]["content"]

                requests.post(
                    "https://webexapis.com/v1/messages",
                    headers={
                        "Authorization": f"Bearer {WEBEX_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "roomId": room_id,
                        "markdown": reply
                    }
                )

                room_state.pop(room_id, None)
            else:
                send_card(room_id, get_homepage_card(), markdown="Welcome to Kino")

    elif data["resource"] == "attachmentActions" and data["event"] == "created":
        room_id = data["data"]["roomId"]
        action_id = data["data"]["id"]

        # ✅ Fetch card action data
        action_details = requests.get(
            f"https://webexapis.com/v1/attachment/actions/{action_id}",
            headers={"Authorization": f"Bearer {WEBEX_TOKEN}"}
        ).json()

        action_type = action_details.get("inputs", {}).get("action")
        print("🖱️ User clicked:", action_type)

        if action_type in ["reword", "docs", "diagram", "voice"]:
            room_state[room_id] = action_type

        if action_type == "show_features":
            send_card(room_id, get_feature_selector_card(), markdown="Choose a feature")
        elif action_type == "music":
            # Send options for music type
            send_card(room_id, {
                "type": "AdaptiveCard",
                "version": "1.2",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "What type of music would you like?",
                        "wrap": True
                    },
                    {
                        "type": "ActionSet",
                        "actions": [
                            {
                                "type": "Action.Submit",
                                "title": "🎶 Energy",
                                "data": {"action": "music_energy"}
                            },
                            {
                                "type": "Action.Submit",
                                "title": "🌌 Chill",
                                "data": {"action": "music_chill"}
                            },
                            {
                                "type": "Action.Submit",
                                "title": "🌬️ White Noise",
                                "data": {"action": "music_white_noise"}
                            }
                        ]
                    }
                ]
            }, markdown="Choose your music type")
        else:
            fixed_responses = {
                "music": "🎵 Great choice! Here's a focus playlist: https://example.com/focus-music",
                "reword": "📚 Drop your text in the chat, and I'll help reword it for clarity.",
                "docs": "🔍 Let's look up the official documentation. What topic do you need help with?",
                "diagram": "✏️ Ready to sketch. Describe what you want visualised.",
                "voice": "🎙️ Voice mode isn't ready yet—but you'll be able to speak to Kino soon!"
            }

            # Handle the new music type actions
            if action_type == "music_energy":
                response_text = "🎶 Here's an energetic playlist for you! Enjoy the music!"
                youtube_link = "https://www.youtube.com/watch?v=wELOA2U7FPQ"  # Energy link
            elif action_type == "music_chill":
                response_text = "🌌 Here's some chill music for you. Relax and enjoy!"
                youtube_link = "https://www.youtube.com/watch?v=26RIzBl0gPQ"  # Chill link
            elif action_type == "music_white_noise":
                response_text = "🌬️ Here's some white noise to help you focus."
                youtube_link = "https://www.youtube.com/watch?v=yLOM8R6lbzg"  # White noise link
            else:
                response_text = fixed_responses.get(action_type, "Sorry, I didn't understand that action.")

                if action_type in ["music_energy", "music_chill", "music_white_noise"]:
                    # Send the final response with the YouTube link
                    send_card(
                        room_id,
                        {
                            "type": "AdaptiveCard",
                            "version": "1.2",
                            "body": [
                                {
                                    "type": "TextBlock",
                                    "text": response_text,
                                    "wrap": True
                                },
                                {
                                    "type": "ActionSet",
                                    "actions": [
                                        {
                                            "type": "Action.OpenUrl",
                                            "title": "Watch on YouTube",
                                            "url": youtube_link
                                        }
                                    ]
                                }
                            ]
                        },
                        markdown="Here's your result"
                    )
                else:
                    # Send a plain text message for non-music tools
                    requests.post(
                        "https://webexapis.com/v1/messages",
                        headers={
                            "Authorization": f"Bearer {WEBEX_TOKEN}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "roomId": room_id,
                            "markdown": response_text
                        }
                    )
    return "OK"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)