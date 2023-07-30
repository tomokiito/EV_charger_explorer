import os
from dotenv import load_dotenv
import requests

def get_charging_stations(api_key, lat, lon):
    distance_unit = "KM"
    distance = 10
    url = f"https://api.openchargemap.io/v3/poi/?key={api_key}&latitude={lat}&longitude={lon}&distanceunit={distance_unit}&distance={distance}"
    response = requests.get(url)
    data = response.json()
    stations = [item['AddressInfo']['Title'] for item in data]
    return stations

def get_geocode(address, api_key):
    url = f"https://us1.locationiq.com/v1/search.php?key={api_key}&q={address}&format=json"
    response = requests.get(url)
    data = response.json()
    return data[0]["lat"], data[0]["lon"]

def get_stations_near(address):
    #API keys
    locationiq_api_key = os.getenv('LOCATIONIQ_API_KEY')
    openchargemap_api_key = os.getenv('OPENCHARGEMAP_API_KEY')

    lat, lon = get_geocode(address, locationiq_api_key)
    stations = get_charging_stations(openchargemap_api_key, lat, lon)

    return stations
