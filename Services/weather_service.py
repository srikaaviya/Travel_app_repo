import os
import requests
from dotenv import load_dotenv

load_dotenv()
def get_weather(city, user_days):
    api_key = os.getenv("WEATHER_API_KEY")
    res = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric")

    if res.status_code == 200:
        data = res.json()
        if user_days == 'future':
            min_t, max_t = 0, 0
            temp = 0
            for items in data['list']:
                temp += int(items['main']['temp'])
                min_t += int(items['main']['temp_min'])
                max_t += int(items['main']['temp_max'])
            # Tuple Return: (Formatted String, Raw Temp)
            return (f"{int(temp // 40)}°C (min {(min_t // 40)}°C / max {(max_t // 40)}°C)", int(temp // 40))
        else:
            current = data['list'][0]
            desc = current['weather'][0]['description']
            temp = int(current['main']['temp'])
            return (desc, temp)
    return None