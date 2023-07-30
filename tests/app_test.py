import pytest

from app.app import app as flask_app  # your application's Flask object
from app.forms import SearchForm
from app.services import get_stations_near

@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()

def test_search(client):
    response = client.get('/')
    assert response.status_code == 200