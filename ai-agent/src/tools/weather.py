"""
src/tools/weather.py
Real-time live weather fetching tool (Zero API keys required).
"""

import urllib.request
import urllib.parse
import json
import re

def get_live_weather(location: str) -> str:
    """
    Fetches real-time weather, temperature, humidity, wind, and forecast
    using lightweight, direct plain-text and JSON endpoints.
    """
    clean_loc = re.sub(r'^(what is|current|weather in|weather for|weather)\s+', '', location, flags=re.IGNORECASE).strip()
    encoded_loc = urllib.parse.quote(clean_loc)

    # Strategy 1: wttr.in formatted live string
    try:
        url = f"https://wttr.in/{encoded_loc}?format=%l:+%C+%t,+Humidity:+%h,+Wind:+%w"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            text = response.read().decode("utf-8").strip()
            if text and "Unknown location" not in text and "<html" not in text:
                return f"Live Weather Data for {clean_loc}:\n{text}"
    except Exception:
        pass

    # Strategy 2: Open-Meteo Geocoding + Direct Forecast API fallback
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_loc}&count=1"
        req = urllib.request.Request(geo_url, headers={"User-Agent": "NovaAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            geo_data = json.loads(response.read().decode("utf-8"))
            if not geo_data.get("results"):
                return ""
            
            res = geo_data["results"][0]
            lat, lon = res["latitude"], res["longitude"]
            city_name = f"{res.get('name', clean_loc)}, {res.get('country', '')}"

        forecast_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m"
        )
        req = urllib.request.Request(forecast_url, headers={"User-Agent": "NovaAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            curr = data.get("current", {})
            
            temp = curr.get("temperature_2m")
            feels_like = curr.get("apparent_temperature")
            humidity = curr.get("relative_humidity_2m")
            wind = curr.get("wind_speed_10m")
            rain = curr.get("precipitation")

            return (
                f"Live Meteorological Data for {city_name}:\n"
                f"- Temperature: {temp}°C (Feels like: {feels_like}°C)\n"
                f"- Relative Humidity: {humidity}%\n"
                f"- Precipitation: {rain} mm\n"
                f"- Wind Speed: {wind} km/h"
            )
    except Exception as e:
        return f"Weather retrieval error: {e}"