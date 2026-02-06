# PostgreSQL Migration Experience

## Project Context
Migrated the Travel App database from **SQLite** to **PostgreSQL** to gain experience with production-grade databases.

---

## Behavioral Interview Talking Points

### 1. Why PostgreSQL?
- SQLite is file-based, good for development but not scalable for production
- PostgreSQL is more robust, supports concurrent connections, and is industry-standard
- Planning to deploy on Heroku, which provides PostgreSQL natively

### 2. Challenges Faced & How I Solved Them

#### Challenge: Different SQL Syntax
- **Problem:** SQLite uses `?` placeholders, PostgreSQL uses `%s`
- **Solution:** Updated all queries in `database.py` to use `%s`

#### Challenge: Getting Last Insert ID
- **Problem:** SQLite uses `cursor.lastrowid`, PostgreSQL doesn't have this
- **Solution:** Used `RETURNING id` clause and `fetchone()[0]`

```python
# SQLite way (doesn't work in PostgreSQL)
cursor.execute('INSERT INTO trips...')
last_id = cursor.lastrowid

# PostgreSQL way
cursor.execute('INSERT INTO trips(...) VALUES (...) RETURNING id', (...))
last_id = cursor.fetchone()[0]
```

#### Challenge: Row Access Changed
- **Problem:** `sqlite3.Row` returns dictionary-like rows; PostgreSQL returns tuples
- **Solution:** Used `RealDictCursor` from `psycopg2.extras` to get dictionary-style access

```python
from psycopg2.extras import RealDictCursor
cursor = conn.cursor(cursor_factory=RealDictCursor)
```

#### Challenge: Connection Syntax Differences
- **Problem:** SQLite connects to a file; PostgreSQL needs host, port, user, database
- **Solution:** Configured connection with proper parameters

```python
# SQLite
conn = sqlite3.connect("travel.db")

# PostgreSQL
conn = psycopg2.connect(
    dbname="travel_app_db",
    user="username",
    host="localhost",
    port="5432"
)
```

#### Challenge: API Error Handling
- **Problem:** AI quota exceeded error wasn't displaying properly after migration
- **Root Cause:** Not a PostgreSQL issue—discovered during debugging that app architecture had changed
- **Solution:** Added early error detection to show user-friendly messages

### 3. Data Migration
- Wrote a Python script to read from SQLite and insert into PostgreSQL
- Handled foreign key constraints by preserving original IDs
- Used `setval()` to reset PostgreSQL sequences after migration

---

## Technical Skills Demonstrated
- PostgreSQL installation and configuration (Homebrew, `psql`)
- Python database connectivity (`psycopg2`)
- Data migration between different database systems
- Debugging and root cause analysis
- Understanding of database abstractions (why `database.py` made migration easier)

---

## Key Takeaways
1. **Abstraction is powerful** – Having all DB code in `database.py` made migration manageable
2. **Test thoroughly** – The tuple vs dictionary issue only appeared at runtime
3. **Understand your tools** – Different databases have different conventions
4. **Debug systematically** – Traced the "London" issue back to refactored app code, not PostgreSQL
