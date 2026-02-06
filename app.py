import os
import json
import markdown2
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect

# --- IMPORTS FROM OUR NEW MODULES ---
import database
# Note: User created "Services" folder (Capital S), so we import from there.
from Services import weather_service, ai_service

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Initialize DB on start
# database.create_db()

@app.route("/", methods=["GET", "POST"])
def index():
    history = []

    if request.method == "GET":
        session.clear()
        return render_template("index.html", chat_history=[])

    if request.method == "POST":
        user_input = request.form.get("user_input")
        
        # --- SCENARIO 1: ANSWERING THE QUESTION ---
        if session.get('awaiting_preference'):
            trip_id = session.get('current_trip_id')
            
            # Use database module
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

            # Generate Final List
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
            
            # Use AI Service
            ai_response_text = ai_service.ask_gemini(weather_prompt)
            clean_html_response = markdown2.markdown(ai_response_text)
            
            database.save_messages(trip_id, 'assistant', clean_html_response)
            session.pop('awaiting_preference', None)

        # --- SCENARIO 2: NEW REQUEST ---
        else:
            # 1. Analyze Input (Using AI Service)
            analysis_prompt = f"""
                Analyze this travel input: "{user_input}"
                Rules:
                    1. If country mentioned, pick popular city.
                    2. Return JSON: {{"is_valid": true, "city": "Name", "timeline": "now/future"}}
            """
            raw_json = ai_service.ask_gemini(analysis_prompt)
            
            # Handle errors
            if "⚠️" in raw_json or "Sorry" in raw_json or "unavailable" in raw_json:
                if 'current_trip_id' not in session:
                    new_trip_id = database.add_trip_details("Unknown", "Unknown", "Error")
                    session['current_trip_id'] = new_trip_id
                    session.modified = True
                database.save_messages(session['current_trip_id'], 'user', user_input)
                database.save_messages(session['current_trip_id'], 'assistant', raw_json)
                history = database.get_chat_history(session['current_trip_id'])
                return render_template("index.html", chat_history=history)
            
            # Quick cleanup to ensure JSON parsing works
            try:
                clean_json = raw_json.replace("```json", "").replace("```", "")
                data = json.loads(clean_json)
                city = data.get("city", "London")
                user_timeline = data.get("timeline", "now")
            except:
                city, user_timeline = "London", "now"

            # 2. Get Weather (Using Weather Service)
            # Returns Tuple: (description_str, temp_int)
            weather_data = weather_service.get_weather(city, user_timeline)
            
            if weather_data:
                weather_desc, temp_val = weather_data
                weather_info = f"{weather_desc}, {temp_val}°C"
            else:
                weather_info = "Unknown"
                temp_val = 20

            # 3. Save Initial Trip
            if 'current_trip_id' not in session:
                new_trip_id = database.add_trip_details(city, weather_info, "Pending...")
                session['current_trip_id'] = new_trip_id
                session.modified = True
            
            active_id = session['current_trip_id']
            database.save_messages(active_id, 'user', user_input)

            # 4. Agent Check logic
            weather_lower = weather_info.lower()
            if ("rain" in weather_lower or "snow" in weather_lower or 
                "drizzle" in weather_lower or "storm" in weather_lower or temp_val < 0):
                
                reason = "snow/rain" if "snow" in weather_lower or "rain" in weather_lower else "freezing temperatures"
                agent_question = f"I see {reason} ({weather_info}) in {city}. Are you planning mostly **Indoor** or **Outdoor** activities?"
                
                html_question = markdown2.markdown(agent_question)
                database.save_messages(active_id, 'assistant', html_question)
                session['awaiting_preference'] = True
                
            else:
                # Normal Flow
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
def reset():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)