import pytest

from EV_charger_explorer.app.app import app as flask_app

from EV_charger_explorer.app.services import delete_station_from_database



@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_search(client):
    # Test that the Flask app is responding correctly to GET requests
    response = client.get('/')
    assert response.status_code == 200

def test_register_station_success(client):
    # sample data
    station_data = {
        'Amps': 16,
        'Comments': 'kW power is an estimate based on the connection type',
        'ConnectionType': 'Type 1 (J1772)',
        'ConnectionTypeID': 1,
        'CurrentType': 'AC (Single-Phase)',
        'CurrentTypeID': 10,
        'ID': 249057,
        'Latitude': 45.519169,
        'Level': 'Level 2 : Medium (Over 2kW)',
        'LevelID': 2,
        'Longitude': -122.675761,
        'PowerKW': 3.7,
        'Quantity': 6,
        'Reference': None,
        'StatusType': 'Operational',
        'StatusTypeID': 50,
        'Title': 'Smart Park - 3rd & Alder',
        'Voltage': 230
    }
    response = client.post('/register', json=station_data)
    response_data = response.get_json()
    station_object_id = response_data['station_object_id']

    # Delete the test data
    delete_station_from_database(flask_app.config['MONGODB_URI'], station_object_id)

    assert response.status_code == 200
    assert response_data['message'] == "Data registered successfully!"
    


def test_register_station_failure(client):
    invalid_station_data = {
        'Amps': 16,
        'Comments': 'Missing crucial data',
    }
    response = client.post('/register', json=invalid_station_data)
    assert response.status_code == 400
    assert response.get_json()['error'] == "Failed to register data - missing required fields"