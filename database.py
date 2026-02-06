import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    conn = psycopg2.connect(
        dbname="travel_app_db",
        user="srikaaviyaramadeve",
        host="localhost",
        port="5432"
    )
    return conn

def add_trip_details(city, weather, essentials):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO trips(city, weather, essentials) VALUES (%s,%s,%s) RETURNING id',
            (city, weather, essentials)
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