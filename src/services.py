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
    # Use your actual API keys here
    locationiq_api_key = "pk.516fd8c75f0b501134144f0fca6169c0"
    openchargemap_api_key = "4be6f4c9-015c-4507-bc70-e40ee82d3919"

    lat, lon = get_geocode(address, locationiq_api_key)
    stations = get_charging_stations(openchargemap_api_key, lat, lon)

    return stations
