import os
import requests
from collections import defaultdict

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId


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
    distance = 1
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
            "Comments": get_value_safe(item, 'Connections', 0, 'Comments'),
            "Latitude": get_value_safe(item, 'AddressInfo', 'Latitude'),
            "Longitude": get_value_safe(item, 'AddressInfo', 'Longitude')
        }
        stations.append(station_info)
    return stations



def get_geocode(address, api_key):
    url = f"https://us1.locationiq.com/v1/search.php?key={api_key}&q={address}&format=json"
    response = requests.get(url)
    data = response.json()
    return data[0]["lat"], data[0]["lon"]


def get_country(latitude, longitude, api_key):
    url = f"https://us1.locationiq.com/v1/reverse.php?key={api_key}&lat={latitude}&lon={longitude}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        country = data.get('address', {}).get('country')
        return country
    else:
        print(f"Error fetching data: {response.text}")
        return None


def get_stations_near(address):
    #API keys
    locationiq_api_key = os.getenv('LOCATIONIQ_API_KEY')
    openchargemap_api_key = os.getenv('OPENCHARGEMAP_API_KEY')

    lat, lon = get_geocode(address, locationiq_api_key)
    stations = get_charging_stations(openchargemap_api_key, lat, lon)

    return stations


def autocomplete_address(query):
    api_key = os.getenv('LOCATIONIQ_API_KEY')
    url = f'https://api.locationiq.com/v1/autocomplete'
    params = {
        'key': api_key,
        'q': query,
        'limit': 5,
        'dedupe': 1
    }
    response = requests.get(url, params=params)
    return response.json()


def register_to_database(uri, station_data):
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client.get_database('Cluster0') 
    collection = db.stations

    try:
        print("Data to be registered:", station_data) 
        print("Data type:", type(station_data)) 
        # Insert data
        result = collection.insert_one(station_data)
        print("Data registered successfully!")
        return True, result.inserted_id
    except Exception as e:
        print(e)
        return False
    finally:
        client.close()


def get_stations_from_database(uri):
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client.get_database('Cluster0')
    collection = db.stations
    stations = list(collection.find({}))
    # Convert ObjectId to string
    for station in stations:
        station['_id'] = str(station['_id'])
    client.close()
    return stations


def delete_station_from_database(uri, station_id):
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client.get_database('Cluster0')
    collection = db.stations

    try:
        # Delete data by _id
        result = collection.delete_one({"_id": ObjectId(station_id)})
        if result.deleted_count > 0:
            print(f"Data deleted successfully!")
            return True
        else:
            print(f"No data found for deletion!")
            return False
    except Exception as e:
        print(e)
        return False
    finally:
        client.close()


def analyze_stations(stations):
    # Initialize analysis variables
    charging_levels = {}
    total_power = 0
    status_types = defaultdict(int)  # Initialize as defaultdict

    # Perform analysis for each station
    for station in stations:

        # Charging levels analysis
        level = station['Level']
        charging_levels[level] = charging_levels.get(level, 0) + 1

        # Determine how to access PowerKW value
        power_kw = station['PowerKW']
        if power_kw is None:
            power_kw = 0.0  # Or continue to skip this record
        elif isinstance(power_kw, dict) and '$numberDouble' in power_kw:
            power_kw = float(power_kw['$numberDouble'])
        else:
            power_kw = float(power_kw)

        # Average power supply analysis
        total_power += power_kw

        # Charging stations by status type analysis
        status_type = station['StatusType']
        if status_type is None:
            status_type = 'Unknown'  # Convert None to a string
        status_types[status_type] += 1

        # Regional distribution analysis


    # Return analysis results as a dictionary
    return {
        "charging_levels": charging_levels,
        "average_power": total_power / len(stations) if stations else 0,
        "status_types": dict(status_types)  # Convert defaultdict to regular dict
    }


