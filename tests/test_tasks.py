import pytest
from unittest.mock import patch
import sys
import os

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tasks import make_celery, send_email_task, mail, flask_app

def test_make_celery():
    """Test that make_celery correctly initializes celery, mail, and flask_app."""
    celery_app, test_mail, test_flask_app = make_celery()
    
    assert celery_app is not None
    assert test_mail is not None
    assert test_flask_app is not None
    assert test_flask_app.config['MAIL_SERVER'] == 'smtp.gmail.com'
    assert test_flask_app.config['MAIL_PORT'] == 587
    assert test_flask_app.config['MAIL_USE_TLS'] is True

@patch('tasks.mail.send')
def test_send_email_task(mock_send):
    """Test that send_email_task constructs and sends the correct email."""
    # Test data
    to_email = "test@example.com"
    city = "Tokyo"
    packing_text = "- Passport\n- Camera\n- Comfortable shoes"

    # Call the task function synchronously
    # We call it directly rather than using .delay() or .apply_async() to unit test the core logic
    send_email_task(to_email, city, packing_text)

    # Assert mail.send was called exactly once
    assert mock_send.call_count == 1
    
    # Retrieve the Message object passed to mail.send
    args, kwargs = mock_send.call_args
    msg = args[0]
    
    # Verify the Message attributes
    assert msg.subject == f"🧳 Your Packing List for {city}"
    assert msg.recipients == [to_email]
    assert packing_text in msg.body
    assert city in msg.body
    assert "Hi!" in msg.body
    assert "Travel Assistant" in msg.body
