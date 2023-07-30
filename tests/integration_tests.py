# tests/integration_tests.py
import pytest
from unittest.mock import patch
from app.app import app as flask_app
from app.services import get_stations_near

@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@patch('app.services.get_charging_stations')
@patch('app.services.get_geocode')
def test_search_form_submission(mock_get_geocode, mock_get_charging_stations, client):
    # Given an address
    address = "221B Baker Street, London"

    # Mock the geocoding service to return some coordinates
    mock_get_geocode.return_value = ("51.5074", "0.1278")

    # Mock the charging stations service to return some stations
    mock_get_charging_stations.return_value = ['Station 1', 'Station 2', 'Station 3']

    # When submitting the search form with the address
    response = client.post('/', data={'address': address}, follow_redirects=True)

    # Then the response should be successful
    assert response.status_code == 200

    # And the response should contain the expected charging stations
    expected_stations = get_stations_near(address)
    for station in expected_stations:
        assert station in response.get_data(as_text=True)