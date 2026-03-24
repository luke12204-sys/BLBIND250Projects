"""
Revision: 1.1
Changelog:
- 1.0: Initial release.
- 1.1: Added detailed inline documentation and pedagogical comments for educational clarity.
NOTE: As last time, I will be distinguishing my comments, with a '~'.
"""

import sys  # Allows us to interact with the system (like exiting the program)
import requests  # The industry standard library for making HTTP requests to websites/APIs
from datetime import datetime  # Used to turn "2024-05-20" into a pretty "Mon, May 20"
#~ I was not aware of this datetime library, I thought it was a nice inclusion. 

def get_coordinates(city, state):
    """
    STEP 1: Geocoding.
    APIs usually don't understand "Birmingham, Alabama" directly; they need 
    Latitude and Longitude. We use Open-Meteo's Geocoding API for this.

    ~ I don't feel like this was the best way for the AI to explain this, I think it probably would have been
    ~ more appropriate for it to have specified that this particular API, that we will use for the weather, 
    ~ would not be able to understand something like "Birmingham, Alabama."
    ~ Because, it says that APIs wouldn't understand it, then uses an API that does understand it to convert. 
    ~ I think it's a little too general of a statement. 
    """
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    
    # These parameters tell the API exactly what we are looking for.
    #~ I feel like I genereally understand what it's doing here, but I didn't understand the counting part, 
    #~ so I asked the AI about it, as it was looking at the top 10 in the search, BEFORE it had the context of what state. 
    #~ I specifically asked, if there was a name common enough to make it so that it wouldn't show up if searched.
    #~ And, as is, if you looked up the 11th or lower population city with the same name, it would fail. 
    params = {
        "name": city,
        "count": 50,      # Look at the top 10 matches ~(Originally)
        #~ After finding out that it wouldn't find some places, I looked up what the most common city name was,
        #~ which turned out to be Franklin, wwith some sources stating up to 45 different cities/towns called Franklin.
        #~ The AI stated the API could handle any amount between 1-100. So I changed it to 50 to be safe. 
        "language": "en",
        "format": "json"  # We want the data back in JSON format (like a Python dictionary)
    }

    try:
        # We send the request and wait up to 10 seconds for a response.
        response = requests.get(geocoding_url, params=params, timeout=10)
        
        # This line raises an error if the website is down (e.g., a 404 or 500 error).
        response.raise_for_status()
        
        # Convert the raw text from the website into a Python dictionary.
        data = response.json()

        # If the API found zero results, "results" won't be in the dictionary.
        if "results" not in data:
            return None

        # DISAMBIGUATION LOGIC:
        # We loop through every result the API found (up to 10). ~ Potentially 50 with the changes. 
        for result in data["results"]:
            # 'admin1' is the API's term for State/Province.
            # We check if the country is US AND if the state matches what the user typed.
            if result.get("country_code") == "US" and \
               result.get("admin1", "").lower() == state.lower():
                # If we find a match, we return the coordinates and the "official" name.
                return {
                    "lat": result["latitude"],
                    "lon": result["longitude"],
                    "full_name": f"{result['name']}, {result['admin1']}"
                }
        
        return None # If we finish the loop and nothing matched our state.

    except requests.exceptions.RequestException as e:
        # This catches connection errors, timeouts, and DNS issues.
        print(f"Error connecting to geocoding service: {e}")
        sys.exit(1)

def get_weather_forecast(lat, lon):
    """
    STEP 2: The Weather Request.
    Now that we have GPS coordinates, we ask for the actual 10-day weather.
    """
    weather_url = "https://api.open-meteo.com/v1/forecast"
    
    # We specify the units (Fahrenheit, Inches) in the request so the API does the math for us.
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "temperature_unit": "fahrenheit",
        "precipitation_unit": "inch",
        "timezone": "auto",  # This ensures the dates match the local time of the city.
        "forecast_days": 10
    }

    try:
        response = requests.get(weather_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to weather service: {e}")
        sys.exit(1)

def display_table(location_name, forecast_data):
    """
    STEP 3: Presentation.
    This takes the messy JSON data and turns it into a human-readable table.
    """
    daily = forecast_data["daily"]
    
    print(f"\n10-Day Forecast for: {location_name}")
    print("-" * 65)
    
    # The :<15 syntax means "left-aligned with 15 characters of padding".
    # This keeps our table columns perfectly straight.
    header = f"{'Date':<15} | {'Max Temp (°F)':<15} | {'Min Temp (°F)':<15} | {'Precip (in)':<12}"
    print(header)
    print("-" * 65)

    # We iterate through the list of dates provided by the API.
    for i in range(len(daily["time"])):
        # raw_date is a string like "2024-05-20". 
        # datetime.strptime turns it into a Python object we can manipulate.
        raw_date = datetime.strptime(daily["time"][i], "%Y-%m-%d")
        # .strftime transforms it into "Mon, May 20".
        formatted_date = raw_date.strftime("%a, %b %d")
        
        max_t = daily["temperature_2m_max"][i]
        min_t = daily["temperature_2m_min"][i]
        precip = daily["precipitation_sum"][i]

        # .1f means "float with 1 decimal place". .2f means "2 decimal places".
        print(f"{formatted_date:<15} | {max_t:<15.1f} | {min_t:<15.1f} | {precip:<12.2f}")
    
    print("-" * 65)

def main():
    """
    The 'Orchestrator'. This function controls the flow of the program.
    """
    print("--- US Weather Forecast Finder ---")
    
    # .strip() removes any accidental spaces the user might type before or after the name.
    city = input("Enter the City: ").strip()
    state = input("Enter the State (Full Name): ").strip()

    if not city or not state:
        print("Error: Both city and state are required.")
        return

    # Phase 1: Convert City/State names to GPS coordinates.
    location = get_coordinates(city, state)
    
    if not location:
        print(f"Error: Could not find '{city}, {state}'. Please check the spelling.")
        sys.exit(1)

    # Phase 2: Use those coordinates to get the weather.
    forecast = get_weather_forecast(location["lat"], location["lon"])

    # Phase 3: Print it out.
    display_table(location["full_name"], forecast)

# This is a Python best practice. It ensures the code only runs if you execute
# this file directly, rather than importing it into another script.
if __name__ == "__main__":
    main()