import datetime
import os

import requests

global api_key
api_key = os.getenv("WEATHER_API_KEY", None)


def main():
    pass


def weather_fetch(user_input):
    """Fetches the current weather of an user-inputted city.

    Args:
        city (string): City name, in the format of (City name, Country in 2
        letters.)

    Returns:
        string: A formatted message of the current weather of given city.
        Message can be changed depending on the input:
        - Too many/few arguments.
        - City not found.
        - Invalid format
        - The weather itself.
    """
    command_args = user_input.split(" ", 1)
    print(command_args)
    if len(command_args) <= 1:
        message = "Too few arguments!"
    elif len(command_args) > 2:
        message = "Too many arguments!"
    else:
        city = command_args[1]
        coords = city_coords_fetch(city)

        if coords is False:
            message = "City does not exist!"
        elif coords == "Err-Wrong-Format":
            message = "Invalid format! Must be (City name-Country in 2 letters)"
        else:
            lat, lon = coords
            (
                city_name,
                weather_emoji,
                temp,
                humidity,
                wind_speed,
                weather,
                timezone,
            ) = call_weather_api(lat, lon)

            message = f"""Showing the weather for {city_name}:

Local time: {timezone}.

Current weather is {weather_emoji} {weather}, with a temperature of {(temp)}⁰C.

Wind speed is {wind_speed} km/h.
Humidity is {humidity}%"""

    response = {"text": message}
    return response


def city_coords_fetch(city):
    """Fetches the coordinates of an user-inputted city.

    As stated in OWM's documentation, built-in geocoding (which returns the weather
    using only the city name), will be deprecated soon.

    In order to prevent any future breakages, I built this function to search
    the given city, and return its corresponding coordinates, which will be
    needed for the weather fetching.

    This also does the necessary sanity check (Checks for the syntax of the
    inputted city.)

    Args:
        city (str): City name, in the format of (City name, Country in 2
        letters.)

    Raises:
        ValueError: When the inputted city does not match the format.

    Returns:
        list: Contains the latitude and longitude of the inputted city.
        False: If there is no result.
    """
    try:
        city_name, country = city.split(",")
    except ValueError:
        return "Err-Wrong-Format"

    GEO_API = "http://api.openweathermap.org/geo/1.0/direct"
    geo_params = {
        "appid": api_key,
        "q": f"{city_name.strip()}, {country.strip()}",
    }

    r = requests.get(GEO_API, params=geo_params)

    response = r.json()
    if len(response) == 0:
        return False
    else:
        # Since we asked the user to input the city based on the syntax, we only need the first one.
        result = response[0]
        lat = float(result["lat"])
        lon = float(result["lon"])

    return [lat, lon]


def get_weather_emoji(weather_id):
    """Returns an emoji corresponding to the weather ID.
    A list of the weather ID can be found here:
    https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2

    Reference code: https://realpython.com/build-a-python-weather-app-cli/#format-weather-types-in-different-colors

    Args:
        weather_id (int): The weather ID received from the OWM API.

    Returns:
        str: An emoji corresponding to the weather ID.
    """
    # Weather ID reference:
    THUNDERSTORM = range(200, 300)
    DRIZZLE = range(300, 400)
    RAIN = range(500, 600)
    SNOW = range(600, 700)
    ATMOSPHERE = range(700, 800)
    CLEAR = range(800, 801)
    CLOUDY = range(801, 900)

    if weather_id in THUNDERSTORM:
        emoji = "⛈️"
    elif weather_id in DRIZZLE:
        emoji = "💧"
    elif weather_id in RAIN:
        emoji = "🌧️"
    elif weather_id in SNOW:
        emoji = "❄️"
    elif weather_id in ATMOSPHERE:
        emoji = "🌀"
    elif weather_id in CLEAR:
        emoji = "☀️"
    elif weather_id in CLOUDY:
        emoji = "☁️"
    else:
        emoji = "🌈"

    return emoji


def call_weather_api(lat, lon):
    """Calls the weather api and gathers the relevant informations of
    the weather.

    Args:
        lat (float): Latitude of the given city
        lon (float): Longtitude of the given city

    Returns:
        list: Contains the data of:
        - City name
        - An emoji matches the weather
        - Temperature in Celcius
        - Humidity
        - Wind speed in km/h
        - Current weather.
    """
    API_URL = "https://api.openweathermap.org/data/2.5/weather"
    api_params = {"appid": api_key, "lat": lat, "lon": lon, "units": "metric"}
    r = requests.get(API_URL, params=api_params)

    response = r.json()

    city_name = f"{response['name']}, {response['sys']['country']}"
    weather_id = int(response["weather"][0]["id"])
    weather_emoji = get_weather_emoji(weather_id)
    data_nums = response["main"]
    temp = round(data_nums["temp"])
    humidity = data_nums["humidity"]
    wind_speed = round(response["wind"]["speed"], 1)
    weather = response["weather"][0]["description"]
    timezone = f"{get_date(response['timezone'])}"

    data = [city_name, weather_emoji, temp, humidity, wind_speed, weather, timezone]

    return data


def get_date(timezone):
    """Gets the local time of the inputted city.
    Reference: https://stackoverflow.com/a/67031211

    Args:
        timezone (int): Timezone offset in UTC

    Returns:
        string: Local time in format: day/month/year, hours(24)/minutes
    """
    tz = datetime.timezone(datetime.timedelta(seconds=int(timezone)))
    return datetime.datetime.now(tz=tz).strftime("%d/%m/%Y, %H:%M")


if __name__ == "__main__":
    main()
