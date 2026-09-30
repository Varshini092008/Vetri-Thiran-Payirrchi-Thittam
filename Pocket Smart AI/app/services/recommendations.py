import json
import traceback
import re
from google import genai
from ..config import settings
from ..database import get_db

client = genai.Client(
    api_key=settings.gemini_api_key
)

def clean_ai_text(text):
    # ** ## * ellam remove pannum
    text = text.replace("**", "")
    text = text.replace("##", "")
    text = text.replace("###", "")
    # Extra * remove panni - aakum
    text = re.sub(r'\n\s*\*\s*', '\n- ', text)
    text = re.sub(r'^\s*\*\s*', '- ', text, flags=re.MULTILINE)
    return text.strip()

def get_fallback_suggestion(planner_type, data, error_msg=""):
    if planner_type == "party":
        return f"""
- Food for {data.get('guests', 30)} guests within Rs.{data.get('budget', '10000')}
- Simple hall decoration with lights and balloons
- Sound system with portable bluetooth speaker
- DIY photo corner with fairy lights
- Mocktail and snacks self-serve station
- Games like quiz and karaoke
- Return gifts like keychain or photo print
- Eco friendly plates and cups
"""
    elif planner_type == "home":
        return f"""
- Budget Rs.{data.get('budget', 0)} for simple modern home setup
- Focus on good lighting for {', '.join(data.get('rooms', []))}
- Use space saving furniture
- Light colors for walls
- Storage boxes for small rooms
"""
    else:
        return f"""
- Budget Rs.{data.get('budget', 0)} for {data.get('occasion', 'Wedding')} jewelry
- Style {data.get('style', 'Traditional')} simple designs
- Light weight daily use designs
- Check for hallmark and certification
"""

def run(user_id, planner_type, data, image_bytes=None, mime=None):
    
    if planner_type == "home":
        budget = float(data.get("budget", 0))
        ai_prompt = f"""
You are PocketSmart AI.
Budget: {budget} INR
Rooms: {data.get("rooms", [])}
Style: {data.get("style", "Modern")}
Priorities: {data.get("priorities", "")}

Task: Give 8 to 10 short practical home suggestions.
RULE: Plain text only. No markdown. No ** No * No #. Only use - for points.
"""
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=ai_prompt
            )
            ai_suggestions = clean_ai_text(response.text)
        except Exception as e:
            print(f"REAL ERROR: {e}")
            traceback.print_exc()
            ai_suggestions = get_fallback_suggestion(planner_type, data, str(e))

        result = {
            "title": "Smart Home Suggestions",
            "budget": budget,
            "rooms": data.get("rooms", []),
            "style": data.get("style", "Modern"),
            "priorities": data.get("priorities", ""),
            "suggestions": [ai_suggestions]
        }

    elif planner_type == "party":
        budget = float(data.get("budget", 0))
        guests = int(data.get("guests", 0))
        ai_prompt = f"""
You are PocketSmart AI.
Budget: {budget} INR
Guests: {guests}
Event Type: {data.get("event_type", "Birthday")}
Venue: {data.get("venue", "Home")}
Preferences: {data.get("preferences", "")}

Task: Give 8 to 10 short practical party suggestions.
RULE: Plain text only. No markdown. No ** No * No #. Only use - for points.
Example: - Food: Book mini buffet with biryani
"""
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=ai_prompt
            )
            ai_suggestions = clean_ai_text(response.text)
        except Exception as e:
            print(f"REAL ERROR: {e}")
            traceback.print_exc()
            ai_suggestions = get_fallback_suggestion(planner_type, data, str(e))

        result = {
            "title": "Smart Party Suggestions",
            "budget": budget,
            "guests": guests,
            "event_type": data.get("event_type", "Birthday"),
            "venue": data.get("venue", "Home"),
            "preferences": data.get("preferences", ""),
            "suggestions": [ai_suggestions]
        }

    elif planner_type == "jewelry":
        budget = float(data.get("budget", 0))
        occasion = data.get("occasion", "Wedding")
        style = data.get("style", "Traditional")
        ai_prompt = f"""
You are PocketSmart AI.
Budget: {budget} INR
Occasion: {occasion}
Style: {style}

Task: Give 8 to 10 short practical jewelry suggestions.
RULE: Plain text only. No markdown. No ** No * No #. Only use - for points.
"""
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=ai_prompt
            )
            ai_suggestions = clean_ai_text(response.text)
        except Exception as e:
            print(f"REAL ERROR: {e}")
            traceback.print_exc()
            ai_suggestions = get_fallback_suggestion(planner_type, data, str(e))

        result = {
            "title": "AI Jewelry Suggestions",
            "budget": budget,
            "occasion": occasion,
            "style": style,
            "suggestions": [ai_suggestions]
        }
    else:
        result = {
            "title": "AI Suggestions",
            "suggestions": ["Plan according to your budget and requirements."]
        }

    with get_db() as db:
        cursor = db.execute(
            """
            INSERT INTO recommendations
            (user_id, planner, input_json, result_json)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, planner_type, json.dumps(data), json.dumps(result))
        )
        recommendation_id = cursor.lastrowid

    return {
        "id": recommendation_id,
        "user_id": user_id,
        "type": planner_type,
        "data": result
    }