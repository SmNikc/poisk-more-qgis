import requests


def fetch_weather(api_key, location):
    """Fetch weather data from OpenWeatherMap."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None
