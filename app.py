import os
import json
import re
import markdown2
from datetime import datetime
from flask import Flask, render_template, request, session, redirect
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import Config
from flask_mail import Mail, Message
from tasks import send_email_task
from auth import auth_bp

import database
from Services import weather_service, ai_service


app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp)

database.run_migrations()


@app.route("/health")
def health():
    return "ok", 200


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/", methods=["GET", "POST"])
@jwt_required(locations=["cookies"], optional=True)
def index():
    current_user = get_jwt_identity()

    if request.method == "GET":
        if not current_user:
            return redirect("/login")
        session.clear()
        return render_template("index.html", chat_history=[])

    if not current_user:
        return redirect("/login")

    user_id = int(current_user)
    history = []

    if request.method == "POST":
        user_input = request.form.get("user_input")

        # --- SCENARIO 1: ANSWERING THE QUESTION ---
        if session.get('awaiting_preference'):
            trip_id = session.get('current_trip_id')

            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT city, weather FROM trips WHERE id = %s', (trip_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                session.clear()
                return redirect("/")

            city = row[0]
            weather_desc = row[1]

            database.save_messages(trip_id, 'user', user_input)

            current_date = datetime.now().strftime("%B %d, %Y")
            weather_prompt = f"""
            You are a travel assistant.
            Today is {current_date}.
            Destination: {city}
            Weather: {weather_desc}
            User Preference: {user_input} (The user answered this because of bad weather).
            Instructions:
                1. Create a packing list specifically for {user_input} activities.
                2. Use professional Markdown.
            """

            ai_response_text = ai_service.ask_gemini(weather_prompt)
            clean_html_response = markdown2.markdown(ai_response_text)

            database.save_messages(trip_id, 'assistant', clean_html_response)
            session.pop('awaiting_preference', None)

        # --- SCENARIO 2: NEW REQUEST ---
        else:
            analysis_prompt = f"""
                Analyze this travel input: "{user_input}"
                Rules:
                    1. If country mentioned, pick popular city.
                    2. If a province or state is mentioned, pick its most popular city.
                    3. If a city is mentioned directly, use that city.
                    4. Return ONLY the raw JSON object, no explanation, no markdown, no extra text: {{"is_valid": true, "city": "Name", "timeline": "now/future"}}
            """
            raw_json = ai_service.ask_gemini(analysis_prompt)

            if "⚠️" in raw_json or "Sorry" in raw_json or "unavailable" in raw_json:
                if 'current_trip_id' not in session:
                    new_trip_id = database.add_trip_details("Unknown", "Unknown", "Error", user_id)
                    session['current_trip_id'] = new_trip_id
                    session.modified = True
                database.save_messages(session['current_trip_id'], 'user', user_input)
                database.save_messages(session['current_trip_id'], 'assistant', raw_json)
                history = database.get_chat_history(session['current_trip_id'])
                return render_template("index.html", chat_history=history)

            try:
                clean_json = re.search(r'\{.*?\}', raw_json, re.DOTALL)
                if clean_json:
                    data = json.loads(clean_json.group())
                    city = data.get("city", "Unknown")
                    user_timeline = data.get("timeline", "now")
                else:
                    city, user_timeline = "Unknown", "now"
            except:
                city, user_timeline = "Unknown", "now"

            weather_data = weather_service.get_weather(city, user_timeline)

            if weather_data:
                weather_desc, temp_val = weather_data
                weather_info = f"{weather_desc}, {temp_val}°C"
            else:
                weather_info = "Unknown"
                temp_val = 20

            if 'current_trip_id' not in session:
                new_trip_id = database.add_trip_details(city, weather_info, "Pending...", user_id)
                session['current_trip_id'] = new_trip_id
                session.modified = True

            active_id = session['current_trip_id']
            database.save_messages(active_id, 'user', user_input)

            weather_lower = weather_info.lower()
            if ("rain" in weather_lower or "snow" in weather_lower or
                "drizzle" in weather_lower or "storm" in weather_lower or temp_val < 0):

                reason = "snow/rain" if "snow" in weather_lower or "rain" in weather_lower else "freezing temperatures"
                agent_question = f"I see {reason} ({weather_info}) in {city}. Are you planning mostly **Indoor** or **Outdoor** activities?"

                html_question = markdown2.markdown(agent_question)
                database.save_messages(active_id, 'assistant', html_question)
                session['awaiting_preference'] = True

            else:
                current_date = datetime.now().strftime("%B %d, %Y")
                weather_prompt = f"""
                You are a travel assistant.
                Today is {current_date}.
                Traveling to: {city} ({user_timeline}).
                Weather: {weather_info}.
                Instructions: Create a packing list based on temperature. Use Markdown.
                """
                ai_response = ai_service.ask_gemini(weather_prompt)
                clean_html = markdown2.markdown(ai_response)
                database.save_messages(active_id, 'assistant', clean_html)

    if 'current_trip_id' in session:
        history = database.get_chat_history(session['current_trip_id'])

    return render_template("index.html", chat_history=history)


@app.route("/reset")
@jwt_required(locations=["cookies"], optional=True)
def reset():
    current_user = get_jwt_identity()
    if not current_user:
        return redirect("/login")
    session.clear()
    return redirect("/")


@app.route("/send-email", methods=["POST"])
@jwt_required(locations=["cookies"], optional=True)
def send_email():
    current_user = get_jwt_identity()
    if not current_user:
        return redirect("/login")

    to_email = request.form.get("email")
    trip_id = session.get("current_trip_id")

    if not trip_id or not to_email:
        return redirect("/")

    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT city FROM trips WHERE id = %s', (trip_id,))
    row = cursor.fetchone()
    conn.close()
    city = row[0] if row else "your destination"

    history = database.get_chat_history(trip_id)
    packing_content = "\n\n".join(
        msg["message"] for msg in history if msg["role"] == "assistant"
    )
    packing_text = re.sub(r'<[^>]+>', '', packing_content)

    send_email_task.delay(to_email, city, packing_text)

    return redirect("/?email_sent=1")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
