import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret'
    with app.test_client() as client:
        yield client

# This sets up a mock "client" (like a simulated web browser) that allows tests to
# make requests to the Flask application without actually starting a live web server.


def get_auth_cookie(client, username='testuser', email='test@example.com'):
    """Register a test user and return the JWT token as a cookie."""
    # Try register first, fall back to login if user already exists
    response = client.post('/api/register', json={
        'username': username,
        'email': email,
        'password': 'testpass'
    })
    if response.status_code == 409:
        response = client.post('/api/login', json={
            'email': email,
            'password': 'testpass'
        })
    token = response.get_json()['access_token']
    client.set_cookie('access_token_cookie', token)
    return token


def test_homepage_redirects_without_auth(client):
    """Test that the home page redirects to login when not authenticated."""
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_homepage_loads_with_auth(client):
    """Test that the home page loads when authenticated."""
    get_auth_cookie(client)
    response = client.get('/')
    assert response.status_code == 200
    assert b"Travel Packing Assistant" in response.data


def test_login_page_loads(client):
    """Test that the login page loads without auth."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Travel Assistant" in response.data


def test_reset_route_redirects_without_auth(client):
    """Test that reset redirects to login when not authenticated."""
    response = client.get('/reset')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_reset_route_with_auth(client):
    """Test that the reset route clears the session and redirects."""
    get_auth_cookie(client)

    with client.session_transaction() as sess:
        sess['current_trip_id'] = 1

    response = client.get('/reset', follow_redirects=True)
    assert response.status_code == 200
    assert b"Travel Packing Assistant" in response.data
