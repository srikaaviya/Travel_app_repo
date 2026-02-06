import psycopg2

# Connect to your database
conn = psycopg2.connect(
    dbname="travel_app_db",
    user="srikaaviyaramadeve",  # Replace with your Mac username
    host="localhost",
    port="5432"
)

# Test it
cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())

conn.close()