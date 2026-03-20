import sqlite3
import psycopg2

# Connects to both databases (SQLite and PostgreSQL)
sqlite_conn = sqlite3.connect("travel.db")
sqlite_conn.row_factory = sqlite3.Row

postgres_conn = psycopg2.connect(
    dbname="travel_app_db",
    user="srikaaviyaramadeve",  # Replace with your Mac username
    host="localhost",
    port="5432"
)


# Reads all trips from SQLite
sqlite_cursor = sqlite_conn.cursor()
sqlite_cursor.execute("SELECT * FROM trips")
trips = sqlite_cursor.fetchall()

# Reads all chat_history from SQLite
sqlite_cursor.execute("SELECT * FROM chat_history")
chats = sqlite_cursor.fetchall()


# Inserts them into PostgreSQL
postgres_cursor = postgres_conn.cursor()
for trip in trips:
    postgres_cursor.execute("INSERT INTO trips (id, city, weather, essentials, created_at) VALUES (%s, %s, %s, %s, %s)",
                            (trip['id'], trip['city'], trip['weather'], trip['essentials'], trip['created_at']))


# Inserts them into PostgreSQL
postgres_cursor = postgres_conn.cursor()
for chat in chats:
    postgres_cursor.execute('INSERT INTO chat_history (trip_id, role, message) VALUES (%s, %s, %s)',
                 (chat['trip_id'], chat['role'], chat['message']))


postgres_conn.commit()

postgres_cursor.close()
sqlite_cursor.close()