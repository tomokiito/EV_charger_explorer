import os
from dotenv import load_dotenv
import requests


def get_value_safe(data, *keys):
    try:
        for key in keys:
            if isinstance(data, list) and isinstance(key, int) and key < len(data):
                data = data[key]
            elif isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
        return data
    except TypeError:
        return None

def get_charging_stations(api_key, lat, lon):
    distance_unit = "KM"
    distance = 10
    url = f"https://api.openchargemap.io/v3/poi/?key={api_key}&latitude={lat}&longitude={lon}&distanceunit={distance_unit}&distance={distance}"
    response = requests.get(url)
    data = response.json()

    stations = []
    for item in data:
        station_info = {
            "Title": get_value_safe(item, 'AddressInfo', 'Title'),
            "ID": get_value_safe(item, 'ID'),
            "ConnectionTypeID": get_value_safe(item, 'Connections', 0, 'ConnectionTypeID'),
            "ConnectionType": get_value_safe(item, 'Connections', 0, 'ConnectionType', 'Title'),
            "Reference": get_value_safe(item, 'Connections', 0, 'Reference'),
            "StatusTypeID": get_value_safe(item, 'StatusType', 'ID'),
            "StatusType": get_value_safe(item, 'StatusType', 'Title'),
            "LevelID": get_value_safe(item, 'Connections', 0, 'LevelID'),
            "Level": get_value_safe(item, 'Connections', 0, 'Level', 'Title'),
            "Amps": get_value_safe(item, 'Connections', 0, 'Amps'),
            "Voltage": get_value_safe(item, 'Connections', 0, 'Voltage'),
            "PowerKW": get_value_safe(item, 'Connections', 0, 'PowerKW'),
            "CurrentTypeID": get_value_safe(item, 'Connections', 0, 'CurrentTypeID'),
            "CurrentType": get_value_safe(item, 'Connections', 0, 'CurrentType', 'Title'),
            "Quantity": get_value_safe(item, 'Connections', 0, 'Quantity'),
            "Comments": get_value_safe(item, 'Connections', 0, 'Comments')
        }
        stations.append(station_info)
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
