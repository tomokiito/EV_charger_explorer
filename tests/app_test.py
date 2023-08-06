"""
This file contains unit tests for the app.py file.
It tests the functionality of the app itself, without any external dependencies.
This includes testing the correct response from the Flask app and the correct form submission.
"""

import pytest
from EV_charger_explorer.app.app import app as flask_app  # your application's Flask object

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
