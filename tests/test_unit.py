import pytest
import sys
import os

# Add the parent directory to sys.path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.secret_key = 'test_secret_key'  # Needed for session
    with app.test_client() as client:
        yield client

def test_homepage_loads(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Travel Packing Assistant" in response.data

def test_reset_route(client):
    """Test that the reset route clears the session and redirects."""
    with client.session_transaction() as sess:
        sess['current_trip_id'] = 1
    
    response = client.get('/reset', follow_redirects=True)
    assert response.status_code == 200
    assert b"Travel Packing Assistant" in response.data
