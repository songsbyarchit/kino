from flask import Flask, request
from dotenv import load_dotenv
from cards.homepage import get_homepage_card
from cards.feature_selector import get_feature_selector_card
from utils.webex import send_card
import os, requests, sys
from utils.youtube_search import search_youtube

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
            current_tool = room_state.get(room_id, {}).get("tool")

            if current_tool == "reword":
                user_message_id = data["data"]["id"]
                message_data = requests.get(
                    f"https://webexapis.com/v1/messages/{user_message_id}",
                    headers={"Authorization": f"Bearer {WEBEX_TOKEN}"}
                ).json()
                input_text = message_data.get("text", "")
                room_state[room_id] = {"tool": "reword", "last_input": input_text}

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
                            {"role": "user", "content": f"Rewrite this so it keeps all the technical details but sounds like a smart, playful coworker explaining it over coffee. Be precise but fun. Don't reduce the word count or change the meaning. Keep the technical depth intact as far as possible. {input_text}"}
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

                # 🎛️ Follow-up card to tweak the response
                follow_up_card = {
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "🛠 Want to adjust this response?",
                            "wrap": True,
                            "weight": "Bolder",
                            "size": "Medium"
                        },
                        {
                            "type": "TextBlock",
                            "text": "Choose how you’d like to refine the explanation:",
                            "wrap": True
                        },
                        {
                            "type": "Input.ChoiceSet",
                            "id": "vertical",
                            "style": "compact",
                        "choices": [
                            {"title": "Healthcare", "value": "healthcare"},
                            {"title": "Education", "value": "education"},
                            {"title": "Manufacturing", "value": "manufacturing"},
                            {"title": "Retail", "value": "retail"},
                            {"title": "Government", "value": "government"},
                            {"title": "Technology", "value": "technology"},
                            {"title": "Hospitality", "value": "hospitality"},
                            {"title": "Manufacturing", "value": "manufacturing"}
                        ]
                        },
                        {
                            "type": "ActionSet",
                            "actions": [
                                {
                                    "type": "Action.Submit",
                                    "title": "🔬 More Technical",
                                    "data": {"action": "adjust_tone", "level": "more_technical"}
                                },
                                {
                                    "type": "Action.Submit",
                                    "title": "🎈 Less Technical",
                                    "data": {"action": "adjust_tone", "level": "less_technical"}
                                },
                                {
                                    "type": "Action.Submit",
                                    "title": "🎯 Apply Vertical",
                                    "data": {"action": "apply_vertical"}
                                },
                                {
                                    "type": "Action.Submit",
                                    "title": "🏠 Back to Home",
                                    "data": {"action": "back_home"}
                                }
                            ]
                        }
                    ]
                }

                send_card(room_id, follow_up_card, markdown="Want to tweak the explanation?")

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

        if action_type == "reword":
            room_state[room_id] = {"tool": "reword", "last_input": None}
            requests.post(
                "https://webexapis.com/v1/messages",
                headers={
                    "Authorization": f"Bearer {WEBEX_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "roomId": room_id,
                    "markdown": "📚 Drop your text in the chat, and I'll help reword it for clarity."
                }
            )
            return "OK"


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
                            },
                            {
                            "type": "Action.Submit",
                            "title": "🏠 Back to Home",
                            "data": {"action": "back_home"}
                            }
                        ]
                    }
                ]
            }, markdown="Choose your music type")
        else:
            fixed_responses = {
                "music": "🎵 Great choice! Here's a focus playlist: https://example.com/focus-music",
                "docs": "🔍 Let's look up the official documentation. What topic do you need help with?",
                "diagram": "✏️ Ready to sketch. Describe what you want visualised.",
                "voice": "🎙️ Voice mode isn't ready yet—but you'll be able to speak to Kino soon!"
            }

            if action_type == "music_energy":
                response_text = "🎶 Here's an energetic playlist for you! Enjoy the music!"
                youtube_link = search_youtube("energetic focus music instrumental")
                send_card(room_id, {
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {"type": "TextBlock", "text": response_text, "wrap": True},
                    {
                        "type": "ActionSet",
                        "actions": [
                            {
                                "type": "Action.OpenUrl",
                                "title": "Watch on YouTube",
                                "url": youtube_link
                            },
                            {
                                "type": "Action.Submit",
                                "title": "🏠 Back to Home",
                                "data": {"action": "back_home"}
                            }
                        ]
                    }
                    ]
                }, markdown="Here's your result")

            elif action_type == "music_chill":
                response_text = "🌌 Here's some chill music for you. Relax and enjoy!"
                youtube_link = search_youtube("chill lofi instrumental focus music")
                send_card(room_id, {
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {"type": "TextBlock", "text": response_text, "wrap": True},
                        {
                            "type": "ActionSet",
                            "actions": [
                                {
                                    "type": "Action.OpenUrl",
                                    "title": "Watch on YouTube",
                                    "url": youtube_link
                                },
                                {
                                    "type": "Action.Submit",
                                    "title": "🏠 Back to Home",
                                    "data": {"action": "back_home"}
                                }
                            ]
                        }
                    ]
                }, markdown="Here's your result")

            elif action_type == "music_white_noise":
                response_text = "🌬️ Here's some white noise to help you focus."
                youtube_link = search_youtube("white noise for concentration 1 hour")
                send_card(room_id, {
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {"type": "TextBlock", "text": response_text, "wrap": True},
                        {
                            "type": "ActionSet",
                            "actions": [
                                {
                                    "type": "Action.OpenUrl",
                                    "title": "Watch on YouTube",
                                    "url": youtube_link
                                },
                                {
                                    "type": "Action.Submit",
                                    "title": "🏠 Back to Home",
                                    "data": {"action": "back_home"}
                                }
                            ]
                        }
                    ]
                }, markdown="Here's your result")

            elif action_type == "adjust_tone":
                tone = action_details.get("inputs", {}).get("level", "neutral")
                last_state = room_state.get(room_id)

                if last_state and last_state.get("tool") == "reword":
                    input_text = last_state.get("last_input", "")

                    if tone == "more_technical":
                        prompt = f"Rewrite this in a more technical way, keeping all details and increasing technical depth: {input_text}"
                    elif tone == "less_technical":
                        prompt = f"Rewrite this in a simpler, less technical way for a general audience, but keep the meaning: {input_text}"
                    else:
                        prompt = input_text  # fallback

                    response = requests.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "gpt-3.5-turbo",
                            "messages": [{"role": "user", "content": prompt}]
                        }
                    ).json()

                    updated_reply = response["choices"][0]["message"]["content"]

                    requests.post(
                        "https://webexapis.com/v1/messages",
                        headers={
                            "Authorization": f"Bearer {WEBEX_TOKEN}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "roomId": room_id,
                            "markdown": updated_reply
                        }
                    )

                    # Send follow-up card to let user re-enter the reword tool
                    send_card(room_id, {
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "🔁 Want to try rewording something else?",
                                "wrap": True
                            }
                        ],
                        "actions": [
                            {
                                "type": "Action.Submit",
                                "title": "📚 Back to Reword Tool",
                                "data": {"action": "reword"}
                            }
                        ]
                    }, markdown="Need to reword something else?")

                else:
                    requests.post(
                        "https://webexapis.com/v1/messages",
                        headers={
                            "Authorization": f"Bearer {WEBEX_TOKEN}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "roomId": room_id,
                            "markdown": "⚠️ Sorry, I couldn't find the original message to adjust."
                        }
                    )

            elif action_type == "apply_vertical":
                vertical = action_details.get("vertical") or action_details.get("inputs", {}).get("vertical")
                if not vertical:
                    # show vertical selection card
                    vertical_card = {
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "🎯 Select your target industry for rewording:",
                                "wrap": True
                            },
                            {
                                "type": "Input.ChoiceSet",
                                "id": "vertical",
                                "style": "compact",
                                "isMultiSelect": False,
                                "choices": [
                                    {"title": "Healthcare", "value": "healthcare"},
                                    {"title": "Education", "value": "education"},
                                    {"title": "Manufacturing", "value": "manufacturing"},
                                    {"title": "Finance", "value": "finance"},
                                    {"title": "Retail", "value": "retail"},
                                    {"title": "Other", "value": "other"}
                                ]
                            }
                        ],
                        "actions": [
                            {
                                "type": "Action.Submit",
                                "title": "Apply Vertical",
                                "data": {"action": "apply_vertical"}
                            }
                        ]
                    }

                    send_card(room_id, vertical_card, markdown="Pick your industry so I can tailor it.")
                    return "OK"
                last_state = room_state.get(room_id)

                if last_state and last_state.get("tool") == "reword":
                    input_text = last_state.get("last_input", "")

                    prompt = (
                        f"Rewrite this so it sounds like a helpful technical expert "
                        f"explaining it to someone in the {vertical} industry. "
                        f"Preserve the technical accuracy and detail. Avoid dumbing it down. "
                        f"Make examples and tone specific to {vertical}: {input_text}"
                    )

                    response = requests.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "gpt-3.5-turbo",
                            "messages": [{"role": "user", "content": prompt}]
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

            elif action_type == "back_home":
                room_state.pop(room_id, None)
                send_card(room_id, get_homepage_card(), markdown="Back to home 🏠")

            else:
                # Only show fallback if it wasn't handled by a known action
                if action_type not in ["music_energy", "music_chill", "music_white_noise", "adjust_tone", "apply_vertical"]:
                    response_text = fixed_responses.get(action_type, "Sorry, I didn't understand that action.")

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