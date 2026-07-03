import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Ensure the app directory is in the path so we can import database.py
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_file = str(Path(__file__).resolve().parent.parent)
sys.path.append(db_file)

import database

# The @patch decorator intercepts any calls made to 'psycopg2.connect'
@patch('database.psycopg2.connect')
def test_add_trip_details(mock_connect):
    mock_conn = MagicMock()  # Fake connection object
    mock_cursor = MagicMock()

    # When psycopg2.connect() is called, return our fake connection
    mock_connect.return_value = mock_conn

    # When conn.cursor() is called, return our fake cursor
    mock_conn.cursor.return_value = mock_cursor

    # When cursor.fetchone() is called, return a fake ID (e.g., [42])
    # This simulates the "RETURNING id" part of the SQL query
    mock_cursor.fetchone.return_value = [42]
    # 2. CALL THE FUNCTION YOU ARE TESTING
    # This will now use all the fake objects we set up above
    trip_id = database.add_trip_details("Paris", "Sunny", "Sunscreen")


    assert trip_id == 42
    assert mock_cursor.execute.call_count == 1
    # Ensure cursor.execute was called exactly once

    # Check the exact SQL and parameters that were passed to cursor.execute()
    # call_args[0][0] gets the SQL string, call_args[0][1] gets the tuple of variables
    args, kwargs = mock_cursor.execute.call_args
    sql_query = args[0]
    sql_params = args[1]

    assert "INSERT INTO trips" in sql_query
    assert sql_params == ("Paris", "Sunny", "Sunscreen", None)

    # Ensure it committed the transaction and closed the connection
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('database.psycopg2.connect')
def test_save_messages(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    msg = database.save_messages(42, "user", "Trip details to paris")
    assert mock_cursor.execute.call_count == 1

    args, kwargs = mock_cursor.execute.call_args
    sql_query = args[0]
    sql_params = args[1]

    assert "INSERT INTO chat_history" in sql_query
    assert sql_params == (42, "user", "Trip details to paris")
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


@patch('database.psycopg2.connect')
def test_get_chat_history(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor


    mock_cursor.fetchall.return_value = [{"role": "user", "message": "Hi"}]
    history = database.get_chat_history(42)

    assert mock_cursor.execute.call_count == 1

    args, kwargs = mock_cursor.execute.call_args
    sql_query = args[0]
    sql_params = args[1]

    assert "SELECT role, message FROM chat_history" in sql_query
    assert sql_params == (42,)
    assert history == [{"role": "user", "message": "Hi"}]


