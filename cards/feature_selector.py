def get_feature_selector_card():
    return {
        "type": "AdaptiveCard",
        "version": "1.2",
        "body": [
            {
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": "🧠 Choose a feature"
            },
            {
                "type": "TextBlock",
                "wrap": True,
                "text": "Kino is here to help. What would you like to do right now?"
            },
            {
                "type": "ActionSet",
                "actions": [
                    {
                        "type": "Action.Submit",
                        "title": "🎵 Music",
                        "data": {"action": "music"}
                    },
                    {
                        "type": "Action.Submit",
                        "title": "📚 Reword",
                        "data": {"action": "reword"}
                    },
                    {
                        "type": "Action.Submit",
                        "title": "🎙️ Voice",
                        "data": {"action": "voice"}
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