voice_tile_card = {
    "type": "AdaptiveCard",
    "version": "1.2",
    "body": [
        {
            "type": "TextBlock",
            "text": "🎙️ Voice Recorder",
            "wrap": True,
            "weight": "Bolder",
            "size": "Medium"
        },
        {
            "type": "TextBlock",
            "text": "Choose how you'd like me to respond to your voice message:",
            "wrap": True
        },
        {
            "type": "Input.ChoiceSet",
            "id": "voice_style",
            "style": "compact",
            "isMultiSelect": False,
            "placeholder": "Choose one...",
            "choices": [
                {"title": "🗂️ Organise into Action Steps", "value": "action"},
                {"title": "💖 Supportive Message", "value": "support"},
                {"title": "🔥 Motivation Boost", "value": "motivate"}
            ]
        }
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "🎧 Continue to Recorder",
            "data": {"action": "open_voice_with_style"}
        },
        {
            "type": "Action.Submit",
            "title": "🏠 Back to Home",
            "data": {"action": "back_home"}
        }
    ]
}