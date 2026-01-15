import os, requests, database, json
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect
from google import genai
from datetime import datetime
import markdown2


load_dotenv()
app = Flask(__name__)
SECRET_KEY =  os.getenv("FLASK_SECRET_KEY")   #for session check
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app.secret_key = SECRET_KEY
database.create_db()

def get_weather(city, user_days):
    res = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric")
    if res.status_code == 200:
        data = res.json()
        if user_days == 'future':
            min_t, max_t = 0, 0
            temp = 0
            for items in data['list']:
                temp = int(items['main']['temp'])
                min_t += int(items['main']['temp_min'])
                max_t += int(items['main']['temp_max'])
            return f"{int(temp)}°C (minimum_temp {(min_t // 40)}°C / maximum_temp {(max_t // 40)}°C)"
        else:
            current = data['list'][0]
            desc = current['weather'][0]['description']
            temp = int(current['main']['temp'])
            return f"{desc}, {temp}°C"
    return None

def ask_gemini(prompt):
    response_text = ''
    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        if response.text:
            response_text = response.text.strip()
        else:
            response_text = "model couldn't generate a response."

    except Exception as e:
        if "503" in str(e) or "overloaded" in str(e):
            response_text = "Server Overloaded"
        elif "429" in str(e) or "Quota" in str(e):
            response_text = "(Quota exceeded)"
        else:
            response_text = "Pycharm error"
        print(f"Error: {e}")
    return response_text



@app.route("/", methods=["GET", "POST"])
def index():
    history = []

    if request.method == "GET":
        # first time types the URL, we clear the memory!
        session.clear()
        return render_template("index.html", chat_history=[])


    if request.method == "POST":
        user_input = request.form["user_input"]

        combined_prompt = f"""
            Analyze this travel-related user input: "{user_input}"
            
            Rules:
                1. If the user mentions a whole country (like 'India'), 
            pick the most popular tourist city in that country and use that as the 'city'.
                2. Identify if the timeline is 'now' or 'future'.
                3. Validate if the place is real.
                
                Return ONLY a JSON object:
                {{
                  "is_valid": true/false,
                  "city": "Specific City Name",
                  "timeline": "now/future",
                }}
            
            """
        raw_json = ask_gemini(combined_prompt)
        try:
            data = json.loads(raw_json.replace("```json", "").replace("```", ""))
            is_valid = data.get("is_valid")
            city = data.get("city")
            user_timeline = data.get("timeline")
        except:
            print(f"JSON Parsing failed: {e}")
            # Fallback if AI output isn't perfect JSON
            # setting london as default fallback. if have more api calls,
            # use TODO city = ask_gemini(f"Extract only the city name from: {user_input}")
            is_valid, city, user_timeline = True, "London", "now"


        weather_info = get_weather(city, user_timeline)
        current_date = datetime.now().strftime("%B %d, %Y")

        if weather_info:
            weather_prompt = f"""
            You are a travel assistant.
            
            Today is {current_date}. The user is traveling {user_timeline} to {city}.
            Weather data: {weather_info}.
        
           Instructions:
                1. Based on the temperature {weather_info}, create a specific packing list.
                2. If the weather is over 25°C, focus on summer gear (sunscreen, light linen).
                3. If the weather is under 10°C, focus on layers and coats.
                4. Use professional Markdown with bold headers.
                5. Mention minimum and maximum temperature
            
            Rules:
                - DO NOT display the current date or today's date in your response.
                - Focus only on the packing list and the temperatures provided.
            """
        else:
            weather_prompt = f"You are a travel assistant. Suggest a packing list for: {user_input}"

        ai_response_text = ask_gemini(weather_prompt)
        clean_html_response = markdown2.markdown(ai_response_text)

        # saving to trip table
        if 'current_trip_id' not in session:
            new_trip_id = database.add_trip_details(city, weather_info or "Unknown", clean_html_response)
            session['current_trip_id'] = new_trip_id
            session.modified = True

        # saving to chat_history
        active_id = session['current_trip_id']
        database.save_messages(active_id, 'user', user_input)
        database.save_messages(active_id, 'assistant', clean_html_response)

    if 'current_trip_id' in session:
        history = database.get_chat_history(session['current_trip_id'])

    # RETURN: Pass the history list to the template
    return render_template("index.html", chat_history=history)

@app.route("/reset")
def reset():
    session.clear()     #clears the current trip memory
    return redirect("/")    #This sends the user back to the fresh home page


if __name__ == "__main__":
    app.run(debug=True)
