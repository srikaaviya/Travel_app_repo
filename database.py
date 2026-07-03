import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        conn = psycopg2.connect(database_url)
    else:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "travel_app_db"),
            user=os.getenv("DB_USER", "srikaaviyaramadeve"),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
    return conn


def run_migrations():
    # Retry connection — Postgres may still be starting up in Docker
    for attempt in range(5):
        try:
            conn = get_db_connection()
            break
        except psycopg2.OperationalError:
            if attempt < 4:
                time.sleep(2)
            else:
                raise
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(256) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id SERIAL PRIMARY KEY,
            city VARCHAR(100),
            weather VARCHAR(200),
            essentials TEXT,
            user_id INTEGER REFERENCES users(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            trip_id INTEGER REFERENCES trips(id),
            role VARCHAR(20),
            message TEXT,
            time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# ---- User functions ----

def create_user(username, email, password_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id',
        (username, email, password_hash)
    )
    user_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return user_id


def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT id, username, email, password_hash FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT id, username, email FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    conn.close()
    return user


# ---- Trip functions ----

def add_trip_details(city, weather, essentials, user_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO trips(city, weather, essentials, user_id) VALUES (%s, %s, %s, %s) RETURNING id',
        (city, weather, essentials, user_id)
    )
    last_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return last_id


def save_messages(trip_id, role, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO chat_history (trip_id, role, message) VALUES (%s,%s,%s)',
                 (trip_id, role, message))
    conn.commit()
    conn.close()


def get_chat_history(trip_id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT role, message FROM chat_history WHERE trip_id = %s ORDER BY time_stamp ASC', (trip_id,))
    history = cursor.fetchall()
    conn.close()
    return history
