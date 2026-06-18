# Technical Guide: Migrating from SQLite3 to 



PostgreSQL

"I built an AI-powered Travel Assistant app using Python and Flask. Initially, I used SQLite for rapid prototyping because it's built-in and requires zero setup, but knew it wouldn't be suitable for a production environment like Heroku since It's a file-based database that doesn't handle concurrent users well. To make the app robust and production-ready, I migrated the entire backend to PostgreSQL.

During the migration, I swapped the database driver to `psycopg2` and heavily refactored my database connection layer to use explicit cursors and secure parameterized queries (`%s`). To prevent losing any existing user interactions, I wrote a custom Python script that connected to both databases simultaneously, extracted the data, mapped it to the new PostgreSQL schema, and safely updated the primary key sequences. Because I had abstracted my database logic into its own service layer early on, the migration was seamless and didn't break any of my frontend routing."


---

## 1. Environment Setup

### Install PostgreSQL
Installed PostgreSQL via Homebrew on macOS:
```bash
brew install postgresql@17
brew services start postgresql@17
```

### Install Python Driver
Installed the binary version of the `psycopg2` adapter for PostgreSQL connectivity:
```bash
pip3 install psycopg2-binary
```
Updated the `requirements.txt` file to include `psycopg2-binary`.

---

## 2. Database Creation & Schema Setup

Using the PostgreSQL interactive terminal (`psql`), we created the new database and matching tables exactly like the old SQLite ones, but with PostgreSQL-specific syntax:

```sql
-- 1. Create the database
CREATE DATABASE travel_app_db;

-- 2. Connect to the database
\c travel_app_db

-- 3. Create trips table using SERIAL for auto-incrementing primary key
CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    weather TEXT NOT NULL,
    essentials TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create chat_history table
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER REFERENCES trips(id),
    role TEXT CHECK (role IN ('user', 'assistant')),
    message TEXT,
    time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Differences from SQLite:**
- `integer primary key autoincrement` -> `SERIAL PRIMARY KEY`
- `datetime` -> `TIMESTAMP`
- Foreign keys are defined inline: `trip_id INTEGER REFERENCES trips(id)`

---

## 3. Python Code Changes (`database.py`)

### A. Imports & Connection String
Replaced `sqlite3` with `psycopg2`.

**Before (SQLite):**
```python
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("travel.db")
    conn.row_factory = sqlite3.Row
    return conn
```

**After (PostgreSQL):**
```python
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    conn = psycopg2.connect(
        dbname="travel_app_db",
        user="srikaaviyaramadeve", # Your Mac username
        host="localhost",
        port="5432"
    )
    return conn
```

### B. Executing Queries and Placeholders
PostgreSQL requires explicit usage of `cursor.execute()` and uses `%s` for placeholders instead of `?`.

**Before (SQLite):**
```python
conn.execute('insert into chat_history (trip_id, role, message) values (?,?,?)', (trip_id, role, message))
```

**After (PostgreSQL):**
```python
cursor = conn.cursor()
cursor.execute('INSERT INTO chat_history (trip_id, role, message) VALUES (%s,%s,%s)', (trip_id, role, message))
```

### C. Retrieving the Inserted ID
SQLite used `lastrowid`, but in PostgreSQL, we must append `RETURNING id` to the SQL query and fetch the result.

**Before (SQLite):**
```python
cursor = conn.execute('insert into trips(...) values (...)', (...))
last_id = cursor.lastrowid
```

**After (PostgreSQL):**
```python
cursor = conn.cursor()
cursor.execute('INSERT INTO trips(...) VALUES (...) RETURNING id', (...))
last_id = cursor.fetchone()[0]
```

### D. Preserving Dictionary-Like Rows
To prevent breaking the application's HTML template which relied on accessing row properties by key name (e.g. `chat['message']`):

**Before (SQLite):**
```python
conn.row_factory = sqlite3.Row
# All queries inherently return dictionary-like objects
```

**After (PostgreSQL):**
```python
# Pass RealDictCursor directly to the cursor constructor
cursor = conn.cursor(cursor_factory=RealDictCursor) 
```

---

## 4. Application Changes (`app.py`)

Several quick updates were made where `app.py` directly touched the database objects.

1. **Removed Database Creation Call**: Removed `database.create_db()` since we now manage schemas directly in `psql`.
2. **Updated Local Queries**: Replaced `conn.execute()` with correct cursor methodology.

```python
# Updated direct app.py database hit:
conn = database.get_db_connection()
cursor = conn.cursor()
cursor.execute('SELECT city, weather FROM trips WHERE id = %s', (trip_id,))
row = cursor.fetchone()
conn.close()

# Extracted variables using tuple index format since this cursor wasn't a RealDictCursor
city = row[0]
weather_desc = row[1]
```

---

## 5. Data Migration

A custom Python script (`Notes/migrate_db_data_py.txt`) was written to stream data out of SQLite and insert it into PostgreSQL. 

**Important Data Migration Steps:**
1. Connect to both databases simultaneously.
2. Read tuples out of SQLite using `sqlite3.Row` to easily map keys.
3. explicitly map the original SQLite `id` row onto the PostgreSQL `id` row during the insert `(id, city, weather... ) VALUES (...)` to make sure foreign key relations in `chat_history` didn't break.
4. Update the PostgreSQL ID sequences afterward so `SERIAL` features wouldn't auto-assign duplicate keys:
```sql
-- Ran in psql terminal
SELECT setval('trips_id_seq', (SELECT MAX(id) FROM trips));
```
