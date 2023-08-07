import os
import pytest

from unittest.mock import patch, Mock
from EV_charger_explorer.app.services import get_charging_stations
from EV_charger_explorer.app.services import get_geocode
from EV_charger_explorer.app.services import get_stations_near


@patch('requests.get')
def test_get_charging_stations(mock_get):
    # Define a response body with the expected structure
    mock_response_data = [
        {
            'AddressInfo': {
                'Title': 'Smart Park - 3rd & Alder'
            },
            'ID': 249057,
            'Connections': [
                {
                    'ConnectionTypeID': 1,
                    'ConnectionType': {'Title': 'Type 1 (J1772)'},
                    'Reference': None,
                    'LevelID': 2,
                    'Level': {'Title': 'Level 2 : Medium (Over 2kW)'},
                    'Amps': 16,
                    'Voltage': 230,
                    'PowerKW': 3.7,
                    'CurrentTypeID': 10,
                    'CurrentType': {'Title': 'AC (Single-Phase)'},
                    'Quantity': 6,
                    'Comments': 'kW power is an estimate based on the connection type'
                }
            ],
            'StatusType': {
                'ID': 50,
                'Title': 'Operational'
            }
        }
    ]

    # Set the mock response on the mock object
    mock_get.return_value.json.return_value = mock_response_data

    # Call the function with a test API key and coordinates
    result = get_charging_stations('test_api_key', '0', '0')

    # Define the expected result based on the provided response
    expected_result = [
        {
            'Title': 'Smart Park - 3rd & Alder',
            'ID': 249057,
            'ConnectionTypeID': 1,
            'ConnectionType': 'Type 1 (J1772)',
            'Reference': None,
            'StatusTypeID': 50,
            'StatusType': 'Operational',
            'LevelID': 2,
            'Level': 'Level 2 : Medium (Over 2kW)',
            'Amps': 16,
            'Voltage': 230,
            'PowerKW': 3.7,
            'CurrentTypeID': 10,
            'CurrentType': 'AC (Single-Phase)',
            'Quantity': 6,
            'Comments': 'kW power is an estimate based on the connection type'
        }
    ]

    # Assert that the function returns the expected result
    assert result == expected_result




@patch('EV_charger_explorer.app.services.requests.get')
def test_get_geocode(mock_get):
    mock_response = Mock()
    mock_get.return_value = mock_response
    mock_response.json.return_value = [
        {
            "place_id": "46307064",
            "licence": "https://locationiq.com/attribution",
            "osm_type": "node",
            "osm_id": "3916613190",
            "boundingbox": [
                "51.5237129",
                "51.5238129",
                "-0.1585243",
                "-0.1584243"
            ],
            "lat": "51.5237629",
            "lon": "-0.1584743",
            "display_name": "Sherlock Holmes Museum, 221b, Baker Street, Marylebone, London, Greater London, England, NW1 6XE, United Kingdom",
            "class": "tourism",
            "type": "museum",
            "importance": 0.840064245847336,
            "icon": "https://locationiq.org/static/images/mapicons/tourist_museum.p.20.png"
        },
        {
            "place_id": "149239196",
            "licence": "https://locationiq.com/attribution",
            "osm_type": "way",
            "osm_id": "176312585",
            "boundingbox": [
                "51.5237026",
                "51.5237936",
                "-0.158698",
                "-0.1584418"
            ],
            "lat": "51.523748049999995",
            "lon": "-0.15856988165361335",
            "display_name": "221B, Baker Street, Marylebone, London, Greater London, England, NW1 6XE, United Kingdom",
            "class": "building",
            "type": "house",
            "importance": 0.41009999999999996
        }
    ]

    address = "221B, Baker St, London"
    api_key = "test-api-key"

    expected_lat = "51.5237629"
    expected_lon = "-0.1584743"

    lat, lon = get_geocode(address, api_key)

    assert lat == expected_lat
    assert lon == expected_lon

    mock_get.assert_called_once_with(f"https://us1.locationiq.com/v1/search.php?key={api_key}&q={address}&format=json")




@patch('EV_charger_explorer.app.services.get_charging_stations')
@patch('EV_charger_explorer.app.services.get_geocode')
def test_get_stations_near(mock_get_geocode, mock_get_charging_stations):
    mock_get_geocode.return_value = ("51.5074", "0.1278")  # Assume London coordinates for testing
    mock_get_charging_stations.return_value = ['Station 1', 'Station 2', 'Station 3']  # Mock response

    address = "London, UK"
    stations = get_stations_near(address)

    assert stations == ['Station 1', 'Station 2', 'Station 3']

    locationiq_api_key = os.getenv('LOCATIONIQ_API_KEY')
    openchargemap_api_key = os.getenv('OPENCHARGEMAP_API_KEY')
    mock_get_geocode.assert_called_once_with(address, locationiq_api_key)
    mock_get_charging_stations.assert_called_once_with(openchargemap_api_key, "51.5074", "0.1278")
