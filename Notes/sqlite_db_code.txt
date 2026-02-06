import sqlite3

db_name = "travel.db"

def get_db_connection():
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    conn = get_db_connection()
    conn.execute('''
        create table if not exists trips(
            id integer primary key autoincrement,
            city text not null,
            weather text not null,
            essentials text,
            created_at datetime default current_timestamp
        )
    ''')
    conn.execute('''
        create table if not exists chat_history(
            id integer primary key autoincrement,
            trip_id integer,
            role text check(role in('user', 'assistant')),
            message text,
            time_stamp datetime default current_timestamp,
            foreign key(trip_id) references trips(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_trip_details(city, weather, essentials):
    conn = get_db_connection()
    cursor = conn.execute('insert into trips(city, weather, essentials) values (?,?,?)',
            (city, weather, essentials)
    )
    last_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return last_id

def save_messages(trip_id, role, message):
    conn = get_db_connection()
    conn.execute('insert into chat_history (trip_id, role, message) values (?,?,?)',
                 (trip_id,role,message))
    conn.commit()
    conn.close()


def get_chat_history(trip_id):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.execute('SELECT role, message FROM chat_history WHERE trip_id = ? ORDER BY time_stamp ASC', (trip_id,))
    history = cursor.fetchall()
    conn.close()
    return history

