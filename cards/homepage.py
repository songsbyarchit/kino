def get_homepage_card():
    return {
        "type": "AdaptiveCard",
        "version": "1.2",
        "body": [
            {
                "type": "TextBlock",
                "size": "Large",
                "weight": "Bolder",
                "text": "👋 Welcome to Kino"
            },
            {
                "type": "TextBlock",
                "wrap": True,
                "text": "Your Webex productivity assistant. Kino helps you stay in flow and reduce friction during work with lightweight tools and quick prompts."
            },
            {
                "type": "TextBlock",
                "spacing": "Medium",
                "weight": "Bolder",
                "text": "✨ What Kino can do:"
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "🎵 Music", "value": "Suggests music based on your mood."},
                    {"title": "📚 Reword", "value": "Simplifies technical text using AI."},
                    {"title": "🔍 Docs", "value": "Searches helpful documentation."},
                    {"title": "✏️ Diagram", "value": "Prompts you to sketch ideas."},
                    {"title": "🎙️ Voice", "value": "Optional voice venting tool."}
                ]
            },
            {
                "type": "ActionSet",
                "actions": [
                    {"type": "Action.Submit", "title": "Try a feature", "data": {"action": "help"}}
                ]
            }
        ]
    }